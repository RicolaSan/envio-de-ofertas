"""Barra de filtros e busca para a listagem de ofertas."""

import customtkinter as ctk
from typing import Callable, Optional


class FiltersBar(ctk.CTkFrame):
    """Barra de busca, filtros e ordenação."""

    def __init__(self, master, on_filter: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_filter = on_filter

        self._build_ui()

    def _build_ui(self):
        # Linha 1: Busca
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=12, pady=(12, 8))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍  Buscar por título...",
            height=36,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.search_btn = ctk.CTkButton(
            search_frame,
            text="Buscar",
            width=80,
            height=36,
            command=self._trigger_filter,
        )
        self.search_btn.pack(side="right")

        # Linha 2: Filtros
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkLabel(filter_frame, text="Status:").pack(side="left", padx=(0, 6))

        self.status_var = ctk.StringVar(value="todas")
        status_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["Todas", "Ativas", "Expiradas", "Pendentes", "Inativas"],
            variable=self.status_var,
            command=lambda _: self._trigger_filter(),
            width=120,
            height=32,
        )
        status_menu.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(filter_frame, text="Ordenar:").pack(side="left", padx=(0, 6))

        self.order_var = ctk.StringVar(value="criado_em")
        order_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["Criação", "Início", "Término", "Título"],
            variable=self.order_var,
            command=lambda _: self._trigger_filter(),
            width=120,
            height=32,
        )
        order_menu.pack(side="left", padx=(0, 8))

        self.order_dir_btn = ctk.CTkButton(
            filter_frame,
            text="↓",
            width=36,
            height=32,
            command=self._toggle_order,
        )
        self.order_dir_btn.pack(side="left")

        # Bind Enter no campo de busca
        self.search_entry.bind("<Return>", lambda e: self._trigger_filter())

    def _trigger_filter(self):
        if self.on_filter:
            self.on_filter()

    def _toggle_order(self):
        current = self.order_dir_btn.cget("text")
        self.order_dir_btn.configure(text="↑" if current == "↓" else "↓")
        self._trigger_filter()

    # --- Getters ---

    def get_search_term(self) -> str:
        return self.search_entry.get().strip()

    def get_status_filter(self) -> str:
        mapping = {
            "Todas": "todas",
            "Ativas": "ativas",
            "Expiradas": "expiradas",
            "Pendentes": "pendentes",
            "Inativas": "inativas",
        }
        return mapping.get(self.status_var.get(), "todas")

    def get_order_by(self) -> str:
        mapping = {
            "Criação": "criado_em",
            "Início": "inicio",
            "Término": "fim",
            "Título": "titulo",
        }
        return mapping.get(self.order_var.get(), "criado_em")

    def get_order_desc(self) -> bool:
        return self.order_dir_btn.cget("text") == "↓"

    def reset(self):
        self.search_entry.delete(0, "end")
        self.status_var.set("Todas")
        self.order_var.set("Criação")
        self.order_dir_btn.configure(text="↓")
