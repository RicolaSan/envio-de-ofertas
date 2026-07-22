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
        self.grid_columnconfigure(0, weight=1)

        # Título
        title_text = "✏️ Editar Oferta" if is_edit else "➕ Nova Oferta"
        ctk.CTkLabel(
            self,
            text=title_text,
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, pady=(20, 8), padx=20, sticky="w")

        # Subtítulo
        ctk.CTkLabel(
            self,
            text="Preencha os dados da oferta",
            font=("Segoe UI", 12),
            text_color="#999999",
        ).grid(row=1, column=0, pady=(0, 16), padx=20, sticky="w")

        # Campos
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.grid(row=2, column=0, padx=20, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        # Título
        ctk.CTkLabel(form_frame, text="Título:").grid(row=0, column=0, pady=6, padx=(0, 8), sticky="w")
        self.titulo_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: Alho Roxo")
        self.titulo_entry.grid(row=0, column=1, pady=6, sticky="ew")

        # Data Início (com DatePicker)
        ctk.CTkLabel(form_frame, text="Data Início:").grid(row=1, column=0, pady=6, padx=(0, 8), sticky="w")
        inicio_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        inicio_frame.grid(row=1, column=1, pady=6, sticky="ew")

        self.inicio_label = ctk.CTkLabel(
            inicio_frame,
            text="📅  Selecione a data de início",
            anchor="w",
            text_color="#999999",
        )
        self.inicio_label.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.inicio_btn = ctk.CTkButton(
            inicio_frame,
            text="Selecionar",
            width=90,
            height=30,
            font=("Segoe UI", 11),
            command=lambda: self._abrir_date_picker("inicio"),
        )
        self.inicio_btn.pack(side="right")

        # Data Fim (com DatePicker)
        ctk.CTkLabel(form_frame, text="Data Fim:").grid(row=2, column=0, pady=6, padx=(0, 8), sticky="w")
        fim_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fim_frame.grid(row=2, column=1, pady=6, sticky="ew")

        self.fim_label = ctk.CTkLabel(
            fim_frame,
            text="📅  Selecione a data de fim",
            anchor="w",
            text_color="#999999",
        )
        self.fim_label.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.fim_btn = ctk.CTkButton(
            fim_frame,
            text="Selecionar",
            width=90,
            height=30,
            font=("Segoe UI", 11),
            command=lambda: self._abrir_date_picker("fim"),
        )
        self.fim_btn.pack(side="right")

        # Imagem
        ctk.CTkLabel(form_frame, text="Imagem:").grid(row=3, column=0, pady=6, padx=(0, 8), sticky="w")
        img_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        img_frame.grid(row=3, column=1, pady=6, sticky="ew")

        self.img_path_label = ctk.CTkLabel(
            img_frame,
            text="Nenhum arquivo selecionado",
            text_color="#999999",
            anchor="w",
        )
        self.img_path_label.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.img_btn = ctk.CTkButton(
            img_frame,
            text="📁 Selecionar",
            width=100,
            command=self._select_image,
        )
        self.img_btn.pack(side="right")

        # Ativo
        self._ativo_var = ctk.BooleanVar(value=True)
        self.ativo_check = ctk.CTkCheckBox(
            form_frame,
            text="Oferta ativa",
            variable=self._ativo_var,
        )
        self.ativo_check.grid(row=4, column=1, pady=12, sticky="w")

        # Preview da imagem
        self.preview_label = ctk.CTkLabel(
            form_frame,
            text="",
            width=480,
            height=120,
            corner_radius=6,
        )
        self.preview_label.grid(row=5, column=0, columnspan=2, pady=(8, 0), sticky="ew")

        # Mensagem de erro
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            text_color="#f44336",
            font=("Segoe UI", 11),
            wraplength=460,
        )
        self.error_label.grid(row=3, column=0, pady=(8, 0), padx=20, sticky="w")

        # Botões
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=(16, 20), padx=20, sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="#333333",
            hover_color="#444444",
            width=100,
        ).pack(side="left", padx=(0, 8))

        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Salvar",
            command=self._save,
            width=120,
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
        path = filedialog.askopenfilename(title="Selecionar Imagem", filetypes=filetypes)
        if path:
            self._selected_image = path
            self.img_path_label.configure(text=os.path.basename(path))

            # Preview
            try:
                from PIL import Image
                from customtkinter import CTkImage
                img = Image.open(path)
                img.thumbnail((480, 120), Image.LANCZOS)
                ctk_img = CTkImage(light_image=img, dark_image=img,
                                   size=(img.width, img.height))
                self.preview_label.configure(image=ctk_img, text="")
            except Exception:
                pass

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
