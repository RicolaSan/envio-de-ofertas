"""Barra de filtros moderna para a listagem de ofertas."""

import customtkinter as ctk
from typing import Callable, Optional

COR_BG = "#0d0d0d"
COR_CARD = "#1a1a1a"
COR_TEXTO = "#f5f5f5"
COR_TEXTO_SEC = "#888888"
COR_BORDA = "#2a2a2a"
COR_ACENTO = "#c8a96e"


class FiltersBar(ctk.CTkFrame):
    """Barra compacta com busca, filtros e ordenação."""

    def __init__(self, master, on_filter: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.on_filter = on_filter
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=10)
        container.pack(fill="x")

        # Linha única com busca + filtros
        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=8)

        # Busca
        self.search_entry = ctk.CTkEntry(
            row,
            placeholder_text="🔍  Buscar por título...",
            height=34,
            fg_color=COR_BG,
            border_color=COR_BORDA,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self._trigger_filter())

        # Status
        ctk.CTkLabel(
            row, text="Status:", text_color=COR_TEXTO_SEC,
            font=("Segoe UI", 11),
        ).pack(side="left", padx=(0, 4))

        self.status_var = ctk.StringVar(value="Todas")
        status_menu = ctk.CTkOptionMenu(
            row,
            values=["Todas", "Ativas", "Expiradas", "Pendentes", "Inativas"],
            variable=self.status_var,
            command=lambda _: self._trigger_filter(),
            width=110,
            height=32,
            fg_color=COR_BG,
            button_color=COR_BORDA,
            button_hover_color="#444444",
            dropdown_fg_color=COR_CARD,
            dropdown_hover_color=COR_BORDA,
        )
        status_menu.pack(side="left", padx=(4, 8))

        # Ordenar
        ctk.CTkLabel(
            row, text="Ordenar:", text_color=COR_TEXTO_SEC,
            font=("Segoe UI", 11),
        ).pack(side="left", padx=(0, 4))

        self.order_var = ctk.StringVar(value="Criação")
        order_menu = ctk.CTkOptionMenu(
            row,
            values=["Criação", "Início", "Término", "Título"],
            variable=self.order_var,
            command=lambda _: self._trigger_filter(),
            width=100,
            height=32,
            fg_color=COR_BG,
            button_color=COR_BORDA,
            button_hover_color="#444444",
            dropdown_fg_color=COR_CARD,
            dropdown_hover_color=COR_BORDA,
        )
        order_menu.pack(side="left", padx=(4, 4))

        self.order_dir_btn = ctk.CTkButton(
            row,
            text="↓",
            width=32,
            height=32,
            fg_color=COR_BORDA,
            hover_color="#444444",
            text_color=COR_TEXTO,
            corner_radius=6,
            command=self._toggle_order,
        )
        self.order_dir_btn.pack(side="left")

    def _trigger_filter(self):
        if self.on_filter:
            self.on_filter()

    def _toggle_order(self):
        current = self.order_dir_btn.cget("text")
        self.order_dir_btn.configure(text="↑" if current == "↓" else "↓")
        self._trigger_filter()

    def get_search_term(self) -> str:
        return self.search_entry.get().strip()

    def get_status_filter(self) -> str:
        mapping = {
            "Todas": "todas", "Ativas": "ativas",
            "Expiradas": "expiradas", "Pendentes": "pendentes",
            "Inativas": "inativas",
        }
        return mapping.get(self.status_var.get(), "todas")

    def get_order_by(self) -> str:
        mapping = {
            "Criação": "criado_em", "Início": "inicio",
            "Término": "fim", "Título": "titulo",
        }
        return mapping.get(self.order_var.get(), "criado_em")

    def get_order_desc(self) -> bool:
        return self.order_dir_btn.cget("text") == "↓"

    def reset(self):
        self.search_entry.delete(0, "end")
        self.status_var.set("Todas")
        self.order_var.set("Criação")
        self.order_dir_btn.configure(text="↓")
