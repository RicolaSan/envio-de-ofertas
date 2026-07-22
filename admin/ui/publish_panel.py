"""Painel de publicação com design moderno e feedback visual."""

import customtkinter as ctk
from typing import Callable, Optional

COR_BG = "#0d0d0d"
COR_CARD = "#1a1a1a"
COR_ACENTO = "#c8a96e"
COR_ACENTO_HOVER = "#d4b87a"
COR_TEXTO = "#f5f5f5"
COR_TEXTO_SEC = "#888888"
COR_BORDA = "#2a2a2a"
COR_VERDE = "#4caf50"
COR_VERMELHO = "#f44336"
COR_SUCESSO_BG = "#0d1f0d"
COR_ERRO_BG = "#1f0d0d"


class PublishPanel(ctk.CTkFrame):
    """Painel completo de publicação com destaque visual."""

    def __init__(self, master, on_publish: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.on_publish = on_publish
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Card principal
        main_card = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=12)
        main_card.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_card.grid_columnconfigure(0, weight=1)
        main_card.grid_rowconfigure(1, weight=1)

        # --- Header da seção ---
        header = ctk.CTkFrame(main_card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))

        ctk.CTkLabel(
            header,
            text="🚀  Publicar Site",
            font=("Segoe UI", 18, "bold"),
            text_color=COR_TEXTO,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Gere o site estático e envie para o GitHub Pages",
            font=("Segoe UI", 11),
            text_color=COR_TEXTO_SEC,
        ).pack(anchor="w")

        ctk.CTkFrame(header, height=1, fg_color=COR_BORDA).pack(
            fill="x", pady=(12, 0)
        )

        # --- Área central ---
        center = ctk.CTkFrame(main_card, fg_color="transparent")
        center.grid(row=1, column=0, sticky="nsew", padx=24, pady=12)
        center.grid_columnconfigure(0, weight=1)

        # Instruções
        self.instrucoes = ctk.CTkFrame(center, fg_color="transparent")
        self.instrucoes.pack(fill="x", pady=(0, 16))

        steps = [
            "📦  Gera o site com as ofertas ativas",
            "📤  Envia automaticamente para o GitHub",
            "🌐  GitHub Pages atualiza o site público",
        ]
        for s in steps:
            ctk.CTkLabel(
                self.instrucoes,
                text=s,
                font=("Segoe UI", 12),
                text_color=COR_TEXTO_SEC,
                anchor="w",
            ).pack(fill="x", pady=1)

        # --- Botão de Publicar (grande, destaque) ---
        btn_frame = ctk.CTkFrame(center, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(8, 16))

        self.publish_btn = ctk.CTkButton(
            btn_frame,
            text="🚀  Publicar Agora",
            height=52,
            font=("Segoe UI", 16, "bold"),
            fg_color=COR_ACENTO,
            hover_color=COR_ACENTO_HOVER,
            text_color="#0d0d0d",
            corner_radius=10,
            command=self._publish,
        )
        self.publish_btn.pack(fill="x")

        # --- Status da publicação ---
        self.status_msg = ctk.CTkLabel(
            center,
            text="📋  Pronto para publicar",
            font=("Segoe UI", 12),
            text_color=COR_TEXTO_SEC,
            anchor="w",
        )
        self.status_msg.pack(fill="x", pady=(0, 8))

        # --- Log de eventos ---
        self.log_frame = ctk.CTkFrame(
            center, fg_color=COR_CARD, corner_radius=8,
        )
        self.log_frame.pack(fill="both", expand=True)

        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            height=120,
            font=("Consolas", 11),
            fg_color="transparent",
            text_color=COR_TEXTO_SEC,
            wrap="word",
        )
        self.log_text.pack(fill="both", expand=True, padx=8, pady=6)
        self.log_text.insert("0.0", "Pronto para publicar.\n")
        self.log_text.configure(state="disabled")

    def _publish(self):
        if self.on_publish:
            self.publish_btn.configure(
                state="disabled",
                text="⏳  Publicando...",
                fg_color="#555555",
            )
            self._log("🚀 Iniciando publicação...", COR_ACENTO)
            self.on_publish()

    def _log(self, message: str, color: str = COR_TEXTO_SEC):
        """Registra mensagem no log."""
        pass  # Placeholder - usaremos o callback do main

    def on_publish_start(self):
        """Chamado quando a publicação começa."""
        self.limpar_log()
        self._adicionar_log("⚙️  Gerando site estático...")
        self.status_msg.configure(text="⏳  Publicando...")

    def on_build_complete(self, summary: str):
        """Chamado quando o build termina."""
        self._adicionar_log(f"✅ {summary}")
        self._adicionar_log("📤 Enviando para o GitHub...")

    def on_publish_success(self, output: str):
        """Chamado quando a publicação é bem-sucedida."""
        self._adicionar_log("✅ Publicação concluída com sucesso!")
        if output:
            self._adicionar_log(f"📋 {output}")
        self.publish_btn.configure(
            state="normal",
            text="🚀  Publicar Agora",
            fg_color=COR_ACENTO,
        )
        self.status_msg.configure(
            text="✅  Site publicado com sucesso!",
            text_color=COR_VERDE,
        )
        self.log_frame.configure(fg_color=COR_SUCESSO_BG)

    def on_publish_error(self, error: str):
        """Chamado quando ocorre um erro na publicação."""
        self._adicionar_log(f"❌ {error}")
        self.publish_btn.configure(
            state="normal",
            text="🚀  Tentar Novamente",
            fg_color=COR_ACENTO,
        )
        self.status_msg.configure(
            text="❌  Erro na publicação",
            text_color=COR_VERMELHO,
        )
        self.log_frame.configure(fg_color=COR_ERRO_BG)

    def _adicionar_log(self, message: str):
        """Adiciona mensagem ao log."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def limpar_log(self):
        """Limpa o log de eventos."""
        self.log_text.configure(state="normal")
        self.log_text.delete("0.0", "end")
        self.log_text.configure(state="disabled")
        self.log_frame.configure(fg_color=COR_CARD)
        self.status_msg.configure(
            text="📋  Pronto para publicar",
            text_color=COR_TEXTO_SEC,
        )

    def reset(self):
        """Reseta o painel para o estado inicial."""
        self.limpar_log()
        self.publish_btn.configure(
            state="normal",
            text="🚀  Publicar Agora",
            fg_color=COR_ACENTO,
        )
