"""Seletor de data visual com calendário para o painel administrativo."""

import customtkinter as ctk
from datetime import date, timedelta
from calendar import monthrange, day_name, month_name
from typing import Callable, Optional


MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro",
]

DIAS_PT = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]


class DatePicker(ctk.CTkToplevel):
    """Janela modal com calendário para seleção de data."""

    def __init__(
        self,
        master,
        current_date: Optional[date] = None,
        on_select: Optional[Callable[[date], None]] = None,
        titulo: str = "Selecionar Data",
    ):
        super().__init__(master)
        self.on_select = on_select
        self.titulo = titulo

        hoje = date.today()
        self._selected_date = current_date or hoje
        self._view_year = self._selected_date.year
        self._view_month = self._selected_date.month

        self.title(titulo)
        self.resizable(False, False)
        self.configure(fg_color="#1a1a1a")

        self._build_ui()
        self._render_calendar()

        # Centralizar
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - 300) // 2
        y = master.winfo_rooty() + (master.winfo_height() - 320) // 2
        self.geometry(f"+{x}+{y}")

        self.grab_set()
        self.focus_set()

    def _build_ui(self):
        # --- Cabeçalho de navegação entre meses ---
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12, pady=(12, 4))

        self.btn_prev = ctk.CTkButton(
            nav_frame,
            text="◀",
            width=36,
            height=32,
            fg_color="transparent",
            hover_color="#333333",
            font=("Segoe UI", 14),
            command=self._prev_month,
        )
        self.btn_prev.pack(side="left")

        self.month_label = ctk.CTkLabel(
            nav_frame,
            text="",
            font=("Segoe UI", 15, "bold"),
        )
        self.month_label.pack(side="left", fill="x", expand=True)

        self.btn_next = ctk.CTkButton(
            nav_frame,
            text="▶",
            width=36,
            height=32,
            fg_color="transparent",
            hover_color="#333333",
            font=("Segoe UI", 14),
            command=self._next_month,
        )
        self.btn_next.pack(side="right")

        # --- Grade do calendário ---
        self.cal_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cal_frame.pack(padx=12, pady=(4, 8))

        # Linha de cabeçalho dos dias da semana
        for col, nome_dia in enumerate(DIAS_PT):
            lbl = ctk.CTkLabel(
                self.cal_frame,
                text=nome_dia,
                font=("Segoe UI", 11, "bold"),
                text_color="#999999",
                width=36,
                height=28,
            )
            lbl.grid(row=0, column=col, padx=1, pady=1)

        # --- Botões de ação rápida ---
        quick_frame = ctk.CTkFrame(self, fg_color="transparent")
        quick_frame.pack(fill="x", padx=12, pady=(0, 12))

        hoje = date.today()
        ctk.CTkButton(
            quick_frame,
            text="📅 Hoje",
            width=80,
            height=30,
            font=("Segoe UI", 11),
            command=lambda: self._select_and_close(hoje),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            quick_frame,
            text="➕ 7 dias",
            width=80,
            height=30,
            font=("Segoe UI", 11),
            fg_color="#333333",
            hover_color="#444444",
            command=lambda: self._select_and_close(hoje + timedelta(days=7)),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            quick_frame,
            text="➕ 15 dias",
            width=80,
            height=30,
            font=("Segoe UI", 11),
            fg_color="#333333",
            hover_color="#444444",
            command=lambda: self._select_and_close(hoje + timedelta(days=15)),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            quick_frame,
            text="➕ 30 dias",
            width=80,
            height=30,
            font=("Segoe UI", 11),
            fg_color="#333333",
            hover_color="#444444",
            command=lambda: self._select_and_close(hoje + timedelta(days=30)),
        ).pack(side="left")

    def _render_calendar(self):
        """Renderiza os dias do mês atual na grade."""
        # Atualizar label do mês
        self.month_label.configure(
            text=f"{MESES_PT[self._view_month - 1]} {self._view_year}"
        )

        # Remover botões de dias antigos (linhas 1+)
        for widget in self.cal_frame.grid_slaves():
            row = int(widget.grid_info()["row"])
            if row > 0:
                widget.destroy()

        # Dias do mês
        _, num_dias = monthrange(self._view_year, self._view_month)
        primeiro_dia = date(self._view_year, self._view_month, 1)
        start_col = primeiro_dia.weekday()
        # Ajustar: weekday() retorna 0=seg, mas queremos 0=dom
        start_col = (start_col + 1) % 7

        hoje = date.today()

        for dia in range(1, num_dias + 1):
            data_celula = date(self._view_year, self._view_month, dia)
            row = (start_col + dia - 1) // 7 + 1
            col = (start_col + dia - 1) % 7

            is_selected = data_celula == self._selected_date
            is_today = data_celula == hoje

            # Estilo do botão
            if is_selected:
                fg = "#c8a96e"
                hover = "#d4b87a"
                txt_color = "#1a1a1a"
            elif is_today:
                fg = "#2a2a2a"
                hover = "#3a3a3a"
                txt_color = "#c8a96e"
            else:
                fg = "transparent"
                hover = "#333333"
                txt_color = "#f5f5f5"

            btn = ctk.CTkButton(
                self.cal_frame,
                text=str(dia),
                width=36,
                height=32,
                fg_color=fg,
                hover_color=hover,
                text_color=txt_color,
                font=("Segoe UI", 12, "bold" if (is_selected or is_today) else "normal"),
                corner_radius=16,
                command=lambda d=data_celula: self._select_and_close(d),
            )
            btn.grid(row=row, column=col, padx=1, pady=1)

    def _prev_month(self):
        if self._view_month == 1:
            self._view_month = 12
            self._view_year -= 1
        else:
            self._view_month -= 1
        self._render_calendar()

    def _next_month(self):
        if self._view_month == 12:
            self._view_month = 1
            self._view_year += 1
        else:
            self._view_month += 1
        self._render_calendar()

    def _select_and_close(self, data: date):
        self._selected_date = data
        if self.on_select:
            self.on_select(data)
        self.destroy()

    def get_selected_date(self) -> date:
        return self._selected_date
