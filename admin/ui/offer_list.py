"""Listagem de ofertas com design moderno em cards."""

import customtkinter as ctk
from PIL import Image
import os
from typing import Callable, Optional

from admin.models.offer import Offer

COR_BG = "#0d0d0d"
COR_CARD = "#1a1a1a"
COR_CARD_HOVER = "#222222"
COR_ACENTO = "#c8a96e"
COR_TEXTO = "#f5f5f5"
COR_TEXTO_SEC = "#888888"
COR_BORDA = "#2a2a2a"
COR_VERDE = "#4caf50"
COR_VERMELHO = "#f44336"
COR_LARANJA = "#ff9800"
COR_CINZA = "#757575"


class OfferList(ctk.CTkScrollableFrame):
    """Exibe as ofertas em cards modernos com miniatura e ações."""

    def __init__(self, master, on_edit: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent", scrollbar_button_color=COR_BORDA)
        self.on_edit = on_edit
        self.on_delete = on_delete
        self._cards: dict[str, ctk.CTkFrame] = {}
        self._offer_data: dict[str, Offer] = {}

    def load_offers(self, offers: list[Offer], originals_dir: str = ""):
        """Recarrega a lista com as ofertas fornecidas."""
        for widget in self._cards.values():
            widget.destroy()
        self._cards.clear()
        self._offer_data.clear()

        if not offers:
            empty_frame = ctk.CTkFrame(self, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both", pady=60)

            ctk.CTkLabel(
                empty_frame,
                text="📭",
                font=("Segoe UI", 48),
            ).pack()

            ctk.CTkLabel(
                empty_frame,
                text="Nenhuma oferta encontrada",
                font=("Segoe UI", 16, "bold"),
                text_color=COR_TEXTO_SEC,
            ).pack(pady=(8, 4))

            ctk.CTkLabel(
                empty_frame,
                text='Clique em "➕ Nova Oferta" para cadastrar',
                font=("Segoe UI", 12),
                text_color=COR_TEXTO_SEC,
            ).pack()
            return

        for offer in offers:
            card = self._create_card(offer, originals_dir)
            self._cards[offer.id] = card
            self._offer_data[offer.id] = offer

    def _create_card(self, offer: Offer, originals_dir: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=10)
        card.pack(fill="x", padx=2, pady=3)

        # Container interno
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        # --- Miniatura redonda ---
        thumb_size = 48
        thumb_frame = ctk.CTkFrame(
            inner, width=thumb_size, height=thumb_size,
            corner_radius=thumb_size // 2, fg_color=COR_BORDA,
        )
        thumb_frame.pack(side="left", padx=(0, 12))
        thumb_frame.pack_propagate(False)

        thumb_label = ctk.CTkLabel(
            thumb_frame, text="🛒", font=("Segoe UI", 20),
        )
        thumb_label.pack(expand=True, fill="both")

        # Carregar thumbnail da imagem
        if offer.imagem_original and originals_dir:
            img_path = os.path.join(originals_dir, os.path.basename(offer.imagem_original))
            if os.path.isfile(img_path):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((thumb_size, thumb_size), Image.LANCZOS)
                    from customtkinter import CTkImage
                    ctk_img = CTkImage(
                        light_image=img, dark_image=img,
                        size=(thumb_size, thumb_size),
                    )
                    thumb_label.configure(image=ctk_img, text="")
                except Exception:
                    pass

        # --- Informações ---
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        # Título e badge em linha
        top_line = ctk.CTkFrame(info_frame, fg_color="transparent")
        top_line.pack(fill="x")

        ctk.CTkLabel(
            top_line,
            text=offer.titulo,
            font=("Segoe UI", 13, "bold"),
            text_color=COR_TEXTO,
            anchor="w",
        ).pack(side="left")

        # Badge de status
        if offer.is_ativa:
            status_text, status_color, status_bg = "ATIVA", COR_VERDE, "#0d1f0d"
        elif offer.is_expirada:
            status_text, status_color, status_bg = "EXPIRADA", COR_VERMELHO, "#1f0d0d"
        elif offer.is_pendente:
            status_text, status_color, status_bg = "PENDENTE", COR_LARANJA, "#1f1700"
        else:
            status_text, status_color, status_bg = "INATIVA", COR_CINZA, "#151515"

        badge = ctk.CTkLabel(
            top_line,
            text=status_text,
            font=("Segoe UI", 9, "bold"),
            text_color=status_color,
            fg_color=status_bg,
            corner_radius=4,
            padx=6,
        )
        badge.pack(side="right", padx=(6, 0))

        # Período
        periodo_text = f"📅 {offer.inicio}  →  {offer.fim}"
        ctk.CTkLabel(
            info_frame,
            text=periodo_text,
            font=("Segoe UI", 11),
            text_color=COR_TEXTO_SEC,
            anchor="w",
        ).pack(fill="x")

        # --- Ações ---
        actions_frame = ctk.CTkFrame(inner, fg_color="transparent")
        actions_frame.pack(side="right", padx=(8, 0))

        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️  Editar",
            width=70,
            height=30,
            font=("Segoe UI", 11),
            fg_color="transparent",
            hover_color=COR_CARD_HOVER,
            text_color=COR_TEXTO_SEC,
            corner_radius=6,
            command=lambda o=offer: self._edit_offer(o),
        )
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=32,
            height=30,
            font=("Segoe UI", 12),
            fg_color="transparent",
            hover_color=COR_VERMELHO,
            text_color=COR_TEXTO_SEC,
            corner_radius=6,
            command=lambda o=offer: self._delete_offer(o),
        )
        delete_btn.pack(side="left", padx=2)

        return card

    def _edit_offer(self, offer: Offer):
        if self.on_edit:
            self.on_edit(offer)

    def _delete_offer(self, offer: Offer):
        if self.on_delete:
            self.on_delete(offer)

    def get_offer(self, offer_id: str) -> Optional[Offer]:
        return self._offer_data.get(offer_id)
