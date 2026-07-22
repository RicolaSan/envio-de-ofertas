"""Janela principal do painel administrativo — design moderno."""

import customtkinter as ctk
from PIL import Image
import os
from typing import Optional

from admin.models.offer import Offer
from admin.services.offer_service import OfferService
from admin.services.image_service import ImageService
from admin.services.site_builder_service import SiteBuilderService
from admin.services.publish_service import PublishService
from admin.core.config import AppConfig
from admin.core.git_runner import GitRunner
from admin.ui.offer_list import OfferList
from admin.ui.offer_form import OfferForm
from admin.ui.filters_bar import FiltersBar
from admin.ui.publish_panel import PublishPanel

# Cores do tema premium
COR_BG = "#0d0d0d"
COR_SIDEBAR = "#141414"
COR_CARD = "#1a1a1a"
COR_ACENTO = "#c8a96e"
COR_ACENTO_HOVER = "#d4b87a"
COR_TEXTO = "#f5f5f5"
COR_TEXTO_SEC = "#888888"
COR_BORDA = "#2a2a2a"
COR_VERDE = "#4caf50"
COR_VERMELHO = "#f44336"
COR_LARANJA = "#ff9800"


class MainWindow(ctk.CTk):
    """Janela principal do painel administrativo de ofertas."""

    def __init__(self, config: AppConfig):
        super().__init__()

        self.config = config

        # Inicializar serviços
        self.offer_service = OfferService(
            config.offers_json_path,
            config.originals_dir,
            docs_ofertas_dir=os.path.join(config.site_dir, "ofertas"),
            docs_root=config.site_dir,
        )
        self.image_service = ImageService(
            config.originals_dir,
            config.optimized_dir,
        )
        self.builder = SiteBuilderService(config, self.image_service)
        self.git_runner = GitRunner(
            config.root_dir,
            branch=config.publishing.branch,
        )
        self.publisher = PublishService(self.builder, self.git_runner)

        # Configurar janela
        self.title(f"Painel Administrativo — {config.site.nome}")
        self.geometry("1050x720")
        self.minsize(900, 600)

        # Tema escuro premium
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COR_BG)

        # Variável para controlar aba ativa
        self._aba_ativa = "ofertas"

        self._build_ui()
        self._load_offers()

        # Verificar ambiente Git
        self._check_git()

    # =================================================================
    # CONSTRUÇÃO DA INTERFACE
    # =================================================================

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self._build_sidebar()

        # --- Conteúdo principal ---
        self._build_main_content()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self, width=200, corner_radius=0, fg_color=COR_SIDEBAR,
        )
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        # Logo / Nome do sistema
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(24, 20))

        ctk.CTkLabel(
            logo_frame,
            text="📋",
            font=("Segoe UI", 28),
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_frame,
            text="Admin",
            font=("Segoe UI", 16, "bold"),
            text_color=COR_TEXTO,
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_frame,
            text="Ofertas do Mercado",
            font=("Segoe UI", 10),
            text_color=COR_TEXTO_SEC,
        ).pack(anchor="w")

        # Separador
        ctk.CTkFrame(sidebar, height=1, fg_color=COR_BORDA).pack(
            fill="x", padx=16, pady=(0, 12)
        )

        # Navegação
        nav_items = [
            ("📦  Ofertas", "ofertas", self._mostrar_aba_ofertas),
            ("🚀  Publicar", "publicar", self._mostrar_aba_publicar),
        ]

        self._nav_buttons = {}
        for texto, chave, comando in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=texto,
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color=COR_ACENTO if chave == "ofertas" else "transparent",
                hover_color="#2a2a2a",
                text_color=COR_TEXTO,
                font=("Segoe UI", 13),
                command=lambda k=chave, c=comando: self._trocar_aba(k, c),
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._nav_buttons[chave] = btn

        # Informações do sistema no final da sidebar
        ctk.CTkFrame(sidebar, height=1, fg_color=COR_BORDA).pack(
            fill="x", padx=16, pady=(12, 8)
        )

        info_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        info_frame.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkLabel(
            info_frame,
            text="Status",
            font=("Segoe UI", 10, "bold"),
            text_color=COR_TEXTO_SEC,
        ).pack(anchor="w")

        self.status_label = ctk.CTkLabel(
            info_frame,
            text="🟢 Online",
            font=("Segoe UI", 11),
            text_color=COR_VERDE,
            anchor="w",
        )
        self.status_label.pack(fill="x")

        self.pendentes_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=("Segoe UI", 10),
            text_color=COR_LARANJA,
            anchor="w",
        )
        self.pendentes_label.pack(fill="x")

    def _atualizar_status_pendentes(self):
        """Atualiza indicador de alterações não publicadas."""
        if self.offer_service.alteracoes_pendentes:
            self.pendentes_label.configure(
                text="⚠️  Alterações não publicadas",
                text_color=COR_LARANJA,
            )
            # Destacar botão Publicar na sidebar
            if "publicar" in self._nav_buttons:
                self._nav_buttons["publicar"].configure(
                    text_color=COR_ACENTO,
                )
        else:
            self.pendentes_label.configure(text="")

    def _build_main_content(self):
        # Frame principal do conteúdo
        self.main_content = ctk.CTkFrame(
            self, corner_radius=0, fg_color=COR_BG,
        )
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(2, weight=1)

        # --- Header com stats ---
        self._build_stats_header()

        # --- Container onde as abas serão exibidas ---
        self.aba_container = ctk.CTkFrame(
            self.main_content, fg_color="transparent",
        )
        self.aba_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 16))
        self.aba_container.grid_columnconfigure(0, weight=1)
        self.aba_container.grid_rowconfigure(0, weight=1)

        # Frame da aba "Ofertas"
        self.frame_ofertas = ctk.CTkFrame(self.aba_container, fg_color="transparent")
        self.frame_ofertas.grid(row=0, column=0, sticky="nsew")
        self.frame_ofertas.grid_columnconfigure(0, weight=1)
        self.frame_ofertas.grid_rowconfigure(1, weight=1)
        self._build_aba_ofertas()

        # Frame da aba "Publicar"
        self.frame_publicar = ctk.CTkFrame(self.aba_container, fg_color="transparent")
        self.frame_publicar.grid(row=0, column=0, sticky="nsew")
        self.frame_publicar.grid_columnconfigure(0, weight=1)
        self.frame_publicar.grid_rowconfigure(1, weight=1)
        self._build_aba_publicar()

        # Mostrar aba inicial
        self._mostrar_aba_ofertas()

    def _build_stats_header(self):
        """Cards de estatísticas no topo."""
        stats_frame = ctk.CTkFrame(
            self.main_content, fg_color="transparent",
        )
        stats_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Card Total
        self.stat_total = self._criar_stat_card(
            stats_frame, 0, "📦 Total", "0", COR_TEXTO
        )
        # Card Ativas
        self.stat_ativas = self._criar_stat_card(
            stats_frame, 1, "✅ Ativas", "0", COR_VERDE
        )
        # Card Pendentes
        self.stat_pendentes = self._criar_stat_card(
            stats_frame, 2, "⏳ Pendentes", "0", COR_LARANJA
        )
        # Card Expiradas
        self.stat_expiradas = self._criar_stat_card(
            stats_frame, 3, "❌ Expiradas", "0", COR_VERMELHO
        )

        # Barra de ação abaixo dos stats
        action_bar = ctk.CTkFrame(
            self.main_content, fg_color="transparent",
        )
        action_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=(4, 8))

        # Título da seção
        self.section_title = ctk.CTkLabel(
            action_bar,
            text="📦  Ofertas Cadastradas",
            font=("Segoe UI", 16, "bold"),
            text_color=COR_TEXTO,
            anchor="w",
        )
        self.section_title.pack(side="left")

        # Botão Nova Oferta
        self.new_btn = ctk.CTkButton(
            action_bar,
            text="➕  Nova Oferta",
            height=36,
            corner_radius=8,
            fg_color=COR_ACENTO,
            hover_color=COR_ACENTO_HOVER,
            text_color="#0d0d0d",
            font=("Segoe UI", 12, "bold"),
            command=self._open_new_offer,
        )
        self.new_btn.pack(side="right")

    def _criar_stat_card(self, parent, col, label, valor, cor):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=10)
        card.grid(row=0, column=col, sticky="ew", padx=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", padx=14, pady=10)

        ctk.CTkLabel(
            inner,
            text=label,
            font=("Segoe UI", 11),
            text_color=COR_TEXTO_SEC,
            anchor="w",
        ).pack(fill="x")

        lbl_valor = ctk.CTkLabel(
            inner,
            text=valor,
            font=("Segoe UI", 26, "bold"),
            text_color=cor,
            anchor="w",
        )
        lbl_valor.pack(fill="x")
        return lbl_valor

    def _build_aba_ofertas(self):
        """Conteúdo da aba de Ofertas."""
        # Filtros
        self.filters = FiltersBar(
            self.frame_ofertas,
            on_filter=self._filter_offers,
        )
        self.filters.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Lista de Ofertas
        self.offer_list = OfferList(
            self.frame_ofertas,
            on_edit=self._open_edit_offer,
            on_delete=self._confirm_delete,
        )
        self.offer_list.grid(row=1, column=0, sticky="nsew")

    def _build_aba_publicar(self):
        """Conteúdo da aba de Publicação."""
        # Painel de Publicação em destaque
        self.publish_panel = PublishPanel(
            self.frame_publicar,
            on_publish=self._publish_site,
        )
        self.publish_panel.grid(row=0, column=0, sticky="nsew", pady=0)

    def _trocar_aba(self, chave, comando):
        """Troca a aba ativa e atualiza os botões da sidebar."""
        self._aba_ativa = chave
        for k, btn in self._nav_buttons.items():
            btn.configure(
                fg_color=COR_ACENTO if k == chave else "transparent",
            )
        comando()

    def _mostrar_aba_ofertas(self):
        self.frame_ofertas.tkraise()
        self.section_title.configure(text="📦  Ofertas Cadastradas")
        self._atualizar_stats()

    def _mostrar_aba_publicar(self):
        self.frame_publicar.tkraise()
        self.section_title.configure(text="🚀  Publicação")

    def _atualizar_stats(self):
        """Atualiza os cards de estatísticas."""
        offers = self.offer_service.get_all()
        if not offers:
            return

        from admin.models.offer import OfferCollection
        colecao = OfferCollection(offers)

        self.stat_total.configure(text=str(len(colecao)))
        self.stat_ativas.configure(text=str(len(colecao.active())))
        self.stat_pendentes.configure(text=str(len(colecao.pendentes())))
        self.stat_expiradas.configure(text=str(len(colecao.expiradas())))

    # --- Carregamento ---

    def _load_offers(self):
        offers = self.offer_service.get_all()
        self.offer_list.load_offers(offers, self.config.originals_dir)
        self._atualizar_status_pendentes()

    def _filter_offers(self):
        termo = self.filters.get_search_term()
        status = self.filters.get_status_filter()
        ordenar = self.filters.get_order_by()
        desc = self.filters.get_order_desc()

        results = self.offer_service.search(termo, status, ordenar, desc)
        self.offer_list.load_offers(results, self.config.originals_dir)

    # --- CRUD ---

    def _open_new_offer(self):
        OfferForm(
            self,
            on_save=self._save_new_offer,
            originals_dir=self.config.originals_dir,
        )

    def _open_edit_offer(self, offer: Offer):
        OfferForm(
            self,
            offer=offer,
            on_save=self._save_edit_offer,
            originals_dir=self.config.originals_dir,
        )

    def _save_new_offer(self, titulo, inicio, fim, ativo, imagem, _):
        self.offer_service.criar(titulo, imagem, inicio, fim, ativo)
        self._load_offers()

    def _save_edit_offer(self, titulo, inicio, fim, ativo, imagem, offer):
        self.offer_service.editar(
            offer.id, titulo, inicio, fim, ativo, imagem,
        )
        self._load_offers()

    def _confirm_delete(self, offer: Offer):
        from admin.ui.offer_form import ConfirmDialog
        confirm = ConfirmDialog(
            self,
            titulo=offer.titulo,
            on_confirm=lambda: self._executar_exclusao(offer),
        )

    def _executar_exclusao(self, offer: Offer):
        self.offer_service.excluir(offer.id)
        self._load_offers()
        self._atualizar_stats()

    # --- Publicação ---

    def _publish_site(self):
        self.publish_panel.on_publish_start()

        try:
            collection = self.offer_service.collection
            result = self.publisher.publish(collection)
        except Exception as e:
            self.publish_panel.on_publish_error(f"Exceção: {e}")
            return

        if result.success:
            self.publish_panel.on_build_complete(
                self.builder.get_summary(collection)
            )
            self.publish_panel.on_publish_success(result.output)
            # Limpar indicador de alterações pendentes
            self.offer_service._alteracoes_pendentes = False
            self._atualizar_status_pendentes()
        else:
            self.publish_panel.on_publish_error(result.error)

    # --- Git ---

    def _check_git(self):
        warnings = self.publisher.check_environment()
        if warnings:
            for w in warnings:
                self.publish_panel._log(f"⚠️  {w}")
