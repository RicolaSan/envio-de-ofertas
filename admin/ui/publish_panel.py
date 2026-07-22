"""Painel de publicação com feedback visual do processo."""

import customtkinter as ctk
from typing import Callable, Optional


class PublishPanel(ctk.CTkFrame):
    """Painel inferior com botão de publicação e log de resultados."""

    def __init__(self, master, on_publish: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_publish = on_publish
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # Separador
        separator = ctk.CTkFrame(self, height=1, fg_color="#333333")
        separator.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12)

        # Botão de publicação
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(12, 6), padx=12, sticky="ew")

        self.publish_btn = ctk.CTkButton(
            btn_frame,
            text="🚀  Publicar Site",
            height=44,
            font=("Segoe UI", 14, "bold"),
            fg_color="#c8a96e",
            hover_color="#d4b87a",
            text_color="#1a1a1a",
            corner_radius=8,
            command=self._publish,
        )
        self.publish_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Área de log
        self.status_frame = ctk.CTkFrame(self, fg_color="#151515", corner_radius=6)
        self.status_frame.grid(row=2, column=0, pady=(4, 12), padx=12, sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.log_text = ctk.CTkTextbox(
            self.status_frame,
            height=80,
            font=("Consolas", 11),
            fg_color="transparent",
            text_color="#999999",
            wrap="word",
        )
        self.log_text.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        self.log_text.insert("0.0", "Pronto para publicar.\n")
        self.log_text.configure(state="disabled")

    def _publish(self):
        if self.on_publish:
            self.publish_btn.configure(state="disabled", text="⏳  Publicando...")
            self._log("🚀 Iniciando publicação...")
            self.on_publish()

    def _log(self, message: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def on_publish_start(self):
        """Chamado quando a publicação começa."""
        self._log("⚙️  Gerando site estático...")

    def on_build_complete(self, summary: str):
        """Chamado quando o build termina."""
        self._log(f"✅ {summary}")
        self._log("📤 Enviando para o GitHub...")

    def on_publish_success(self, output: str):
        """Chamado quando a publicação é bem-sucedida."""
        self._log(f"✅ Publicação concluída!")
        if output:
            self._log(output)
        self.publish_btn.configure(state="normal", text="🚀  Publicar Site")

    def on_publish_error(self, error: str):
        """Chamado quando ocorre um erro na publicação."""
        self._log(f"❌ Erro: {error}")
        self.publish_btn.configure(state="normal", text="🚀  Publicar Site")

    def reset(self):
        """Reseta o painel para o estado inicial."""
        self.log_text.configure(state="normal")
        self.log_text.delete("0.0", "end")
        self.log_text.insert("0.0", "Pronto para publicar.\n")
        self.log_text.configure(state="disabled")
        self.publish_btn.configure(state="normal", text="🚀  Publicar Site")
