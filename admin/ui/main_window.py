"""Janela principal do painel administrativo."""

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


class MainWindow(ctk.CTk):
    """Janela principal do painel administrativo de ofertas."""

    def __init__(self, config: AppConfig):
        super().__init__()

        self.config = config

        # Inicializar serviços
        self.offer_service = OfferService(
            config.offers_json_path,
            config.originals_dir,
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
        self.geometry("900x680")
        self.minsize(800, 600)

        # Tema escuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self._build_ui()
        self._load_offers()

        # Verificar ambiente Git
        self._check_git()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        header = ctk.CTkFrame(self, corner_radius=0, height=56)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=f"📋  {self.config.site.nome}",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, padx=16, pady=14, sticky="w")

        # Botão Nova Oferta
        self.new_btn = ctk.CTkButton(
            header,
            text="➕  Nova Oferta",
            height=34,
            command=self._open_new_offer,
        )
        self.new_btn.grid(row=0, column=1, padx=16, pady=10, sticky="e")

        # --- Filtros ---
        self.filters = FiltersBar(self, on_filter=self._filter_offers)
        self.filters.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

        # --- Lista de Ofertas ---
        self.offer_list = OfferList(
            self,
            on_edit=self._open_edit_offer,
            on_delete=self._confirm_delete,
        )
        self.offer_list.grid(row=2, column=0, sticky="nsew", padx=8, pady=4)

        # --- Painel de Publicação ---
        self.publish_panel = PublishPanel(self, on_publish=self._publish_site)
        self.publish_panel.grid(row=3, column=0, sticky="ew", padx=0, pady=0)

    # --- Carregamento ---

    def _load_offers(self):
        offers = self.offer_service.get_all()
        self.offer_list.load_offers(offers, self.config.originals_dir)

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
        result = ctk.CTkInputDialog(
            title="Confirmar Exclusão",
            text=f'Digite "SIM" para excluir:\n{offer.titulo}',
        ).get_input()

        if result and result.strip().upper() == "SIM":
            self.offer_service.excluir(offer.id)
            self._load_offers()

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
        else:
            self.publish_panel.on_publish_error(result.error)

    # --- Git ---

    def _check_git(self):
        warnings = self.publisher.check_environment()
        if warnings:
            for w in warnings:
                self.publish_panel._log(f"⚠️  {w}")
