"""Formulário de cadastro e edição de ofertas."""

import customtkinter as ctk
from tkinter import filedialog
import os
from typing import Callable, Optional
from datetime import date, datetime

from admin.models.offer import Offer
from admin.ui.date_picker import DatePicker


MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro",
]

COR_BG = "#0d0d0d"
COR_CARD = "#1a1a1a"
COR_ACENTO = "#c8a96e"
COR_ACENTO_HOVER = "#d4b87a"
COR_TEXTO = "#f5f5f5"
COR_TEXTO_SEC = "#888888"
COR_BORDA = "#2a2a2a"
COR_VERMELHO = "#f44336"


class ConfirmDialog(ctk.CTkToplevel):
    """Diálogo moderno de confirmação de exclusão."""

    def __init__(self, master, titulo: str, on_confirm: Optional[Callable] = None):
        super().__init__(master)
        self.on_confirm = on_confirm

        self.title("Confirmar Exclusão")
        self.geometry("380x200")
        self.configure(fg_color=COR_BG)
        self.resizable(False, False)

        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 380) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 200) // 2
        self.geometry(f"+{x}+{y}")

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="🗑️  Excluir Oferta",
            font=("Segoe UI", 18, "bold"),
            text_color=COR_TEXTO,
        ).grid(row=0, column=0, pady=(24, 4), padx=24, sticky="w")

        ctk.CTkLabel(
            self,
            text=f'Tem certeza que deseja excluir "{titulo}"?',
            font=("Segoe UI", 12),
            text_color=COR_TEXTO_SEC,
            wraplength=320,
            justify="left",
        ).grid(row=1, column=0, pady=(4, 16), padx=24, sticky="w")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=24, pady=(0, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color=COR_BORDA,
            hover_color="#444444",
            text_color=COR_TEXTO,
            height=36,
            corner_radius=8,
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="🗑️  Excluir",
            fg_color=COR_VERMELHO,
            hover_color="#ff6659",
            text_color=COR_TEXTO,
            height=36,
            corner_radius=8,
            command=self._confirmar,
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

        self.grab_set()
        self.focus_set()

    def _confirmar(self):
        if self.on_confirm:
            self.on_confirm()
        self.destroy()


def _formatar_data(d: date) -> str:
    """Formata uma data no padrão brasileiro legível."""
    return f"{d.day:02d} de {MESES_PT[d.month - 1]} de {d.year}"


def _to_iso(d: date) -> str:
    return d.isoformat()


class OfferForm(ctk.CTkToplevel):
    """Janela modal para criar ou editar uma oferta."""

    def __init__(self, master, offer: Optional[Offer] = None,
                 on_save: Optional[Callable] = None,
                 originals_dir: str = ""):
        super().__init__(master)
        self.offer = offer
        self.on_save = on_save
        self.originals_dir = originals_dir
        self._selected_image: Optional[str] = None
        self._data_inicio: Optional[date] = None
        self._data_fim: Optional[date] = None

        is_edit = offer is not None
        self.title("Editar Oferta" if is_edit else "Nova Oferta")
        self.geometry("520x560")
        self.resizable(False, False)

        # Centralizar
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 520) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 560) // 2
        self.geometry(f"+{x}+{y}")

        self._build_ui(is_edit)

        if is_edit and offer:
            self._populate(offer)

        self.grab_set()
        self.focus_set()

    def _build_ui(self, is_edit: bool):
        self.configure(fg_color=COR_BG)
        self.grid_columnconfigure(0, weight=1)

        # Título com ícone grande
        title_text = "✏️ Editar Oferta" if is_edit else "➕ Nova Oferta"
        ctk.CTkLabel(
            self,
            text=title_text,
            font=("Segoe UI", 20, "bold"),
            text_color=COR_TEXTO,
        ).grid(row=0, column=0, pady=(24, 4), padx=24, sticky="w")

        ctk.CTkLabel(
            self,
            text="Preencha os dados abaixo",
            font=("Segoe UI", 12),
            text_color=COR_TEXTO_SEC,
        ).grid(row=1, column=0, pady=(0, 16), padx=24, sticky="w")

        # Campos
        form_frame = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=10)
        form_frame.grid(row=2, column=0, padx=24, pady=0, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        LABEL_KW = {"text_color": COR_TEXTO_SEC, "font": ("Segoe UI", 12)}
        ENTRY_KW = {
            "fg_color": COR_BG, "border_color": COR_BORDA,
            "text_color": COR_TEXTO,
        }
        BTN_KW = {
            "fg_color": COR_BORDA, "hover_color": "#444444",
            "text_color": COR_TEXTO, "corner_radius": 6,
            "font": ("Segoe UI", 11),
        }

        padding = {"padx": 16, "pady": (10, 0)}

        # Título
        ctk.CTkLabel(form_frame, text="Título:", **LABEL_KW).grid(
            row=0, column=0, **padding, sticky="w")
        self.titulo_entry = ctk.CTkEntry(
            form_frame, placeholder_text="Ex: Alho Roxo", **ENTRY_KW)
        self.titulo_entry.grid(row=0, column=1, **padding, sticky="ew")

        # Data Início
        ctk.CTkLabel(form_frame, text="Data Início:", **LABEL_KW).grid(
            row=1, column=0, **padding, sticky="w")
        inicio_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        inicio_frame.grid(row=1, column=1, **padding, sticky="ew")

        self.inicio_label = ctk.CTkLabel(
            inicio_frame,
            text="📅  Selecione a data de início",
            anchor="w", text_color=COR_TEXTO_SEC,
            font=("Segoe UI", 12),
        )
        self.inicio_label.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.inicio_btn = ctk.CTkButton(
            inicio_frame,
            text="📅", width=40, height=32, **BTN_KW,
            command=lambda: self._abrir_date_picker("inicio"),
        )
        self.inicio_btn.pack(side="right")

        # Data Fim
        ctk.CTkLabel(form_frame, text="Data Fim:", **LABEL_KW).grid(
            row=2, column=0, **padding, sticky="w")
        fim_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fim_frame.grid(row=2, column=1, **padding, sticky="ew")

        self.fim_label = ctk.CTkLabel(
            fim_frame,
            text="📅  Selecione a data de fim",
            anchor="w", text_color=COR_TEXTO_SEC,
            font=("Segoe UI", 12),
        )
        self.fim_label.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.fim_btn = ctk.CTkButton(
            fim_frame,
            text="📅", width=40, height=32, **BTN_KW,
            command=lambda: self._abrir_date_picker("fim"),
        )
        self.fim_btn.pack(side="right")

        # Imagem
        ctk.CTkLabel(form_frame, text="Imagem:", **LABEL_KW).grid(
            row=3, column=0, **padding, sticky="w")
        img_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        img_frame.grid(row=3, column=1, **padding, sticky="ew")

        self.img_path_label = ctk.CTkLabel(
            img_frame,
            text="Nenhum arquivo selecionado",
            text_color=COR_TEXTO_SEC, anchor="w",
            font=("Segoe UI", 12),
        )
        self.img_path_label.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.img_btn = ctk.CTkButton(
            img_frame,
            text="📁 Selecionar", width=90, height=32, **BTN_KW,
            command=self._select_image,
        )
        self.img_btn.pack(side="right")

        # Ativo
        self._ativo_var = ctk.BooleanVar(value=True)
        self.ativo_check = ctk.CTkCheckBox(
            form_frame,
            text="Oferta ativa",
            variable=self._ativo_var,
            text_color=COR_TEXTO,
            font=("Segoe UI", 12),
        )
        self.ativo_check.grid(row=4, column=1, **padding, sticky="w")

        # Preview
        self.preview_label = ctk.CTkLabel(
            form_frame,
            text="",
            width=460, height=100,
            corner_radius=6,
            fg_color=COR_BG,
        )
        self.preview_label.grid(row=5, column=0, columnspan=2,
                                padx=16, pady=(8, 12), sticky="ew")

        # Mensagem de erro
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color=COR_VERMELHO,
            font=("Segoe UI", 11),
            wraplength=460,
        )
        self.error_label.grid(row=3, column=0, pady=(8, 0), padx=24, sticky="w")

        # Botões
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=(16, 24), padx=24, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color=COR_BORDA,
            hover_color="#444444",
            text_color=COR_TEXTO,
            width=100, height=36,
            corner_radius=8,
        ).pack(side="left", padx=(0, 8))

        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="💾  Salvar",
            command=self._save,
            width=120, height=36,
            fg_color=COR_ACENTO,
            hover_color=COR_ACENTO_HOVER,
            text_color=COR_BG,
            corner_radius=8,
            font=("Segoe UI", 12, "bold"),
        )
        self.save_btn.pack(side="right")

    def _abrir_date_picker(self, tipo: str):
        """Abre o DatePicker para início ou fim."""
        data_atual = self._data_inicio if tipo == "inicio" else self._data_fim
        titulo = "Data de Início" if tipo == "inicio" else "Data de Fim"

        DatePicker(
            self,
            current_date=data_atual,
            on_select=lambda d: self._definir_data(tipo, d),
            titulo=titulo,
        )

    def _definir_data(self, tipo: str, data: date):
        """Armazena a data selecionada e atualiza o label."""
        if tipo == "inicio":
            self._data_inicio = data
            self.inicio_label.configure(
                text=f"📅  {_formatar_data(data)}",
                text_color="#f5f5f5",
            )
        else:
            self._data_fim = data
            self.fim_label.configure(
                text=f"📅  {_formatar_data(data)}",
                text_color="#f5f5f5",
            )

    def _atualizar_preview(self, path: str):
        """Atualiza o preview da imagem selecionada."""
        try:
            from PIL import Image
            from customtkinter import CTkImage
            img = Image.open(path)
            img.thumbnail((460, 100), Image.LANCZOS)
            ctk_img = CTkImage(light_image=img, dark_image=img,
                               size=(img.width, img.height))
            self.preview_label.configure(image=ctk_img, text="")
        except Exception:
            pass

    def _populate(self, offer: Offer):
        """Preenche o formulário com dados de uma oferta existente."""
        self.titulo_entry.insert(0, offer.titulo)
        self._ativo_var.set(offer.ativo)

        # Datas
        try:
            data_ini = date.fromisoformat(offer.inicio)
            self._definir_data("inicio", data_ini)
        except (ValueError, TypeError):
            pass

        try:
            data_fim = date.fromisoformat(offer.fim)
            self._definir_data("fim", data_fim)
        except (ValueError, TypeError):
            pass

    def _select_image(self):
        filetypes = [
            ("Imagens", "*.jpg *.jpeg *.png *.webp"),
            ("Todos os arquivos", "*.*"),
        ]
        path = filedialog.askopenfilename(
            title="Selecionar Imagem", filetypes=filetypes,
        )
        if path:
            self._selected_image = path
            self.img_path_label.configure(
                text=os.path.basename(path), text_color=COR_TEXTO,
            )
            self._atualizar_preview(path)

    def _save(self):
        """Valida e dispara o callback de salvamento."""
        titulo = self.titulo_entry.get().strip()
        ativo = self._ativo_var.get()
        imagem = self._selected_image

        # Validações
        from admin.core.validators import validar_titulo

        erro = validar_titulo(titulo)
        if erro:
            self.error_label.configure(text=erro)
            return

        if self._data_inicio is None:
            self.error_label.configure(text="Selecione a data de início.")
            return

        if self._data_fim is None:
            self.error_label.configure(text="Selecione a data de fim.")
            return

        if self._data_fim < self._data_inicio:
            self.error_label.configure(text="A data final não pode ser anterior à data inicial.")
            return

        if not self.offer and not imagem:
            self.error_label.configure(text="Selecione uma imagem para a oferta.")
            return

        inicio = _to_iso(self._data_inicio)
        fim = _to_iso(self._data_fim)

        self.error_label.configure(text="")

        if self.on_save:
            self.on_save(titulo, inicio, fim, ativo, imagem, self.offer)

        self.destroy()
