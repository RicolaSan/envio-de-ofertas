"""Listagem de ofertas com miniaturas, status e ações."""

import customtkinter as ctk
from PIL import Image, ImageTk
import os
from typing import Callable, Optional

from admin.models.offer import Offer


class OfferList(ctk.CTkScrollableFrame):
    """Exibe as ofertas em formato de cards compactos."""

    def __init__(self, master, on_edit: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_edit = on_edit
        self.on_delete = on_delete
        self._cards: dict[str, ctk.CTkFrame] = {}
        self._offer_data: dict[str, Offer] = {}

    def load_offers(self, offers: list[Offer], originals_dir: str = ""):
        """Recarrega a lista com as ofertas fornecidas."""
        # Limpar cards existentes
        for widget in self._cards.values():
            widget.destroy()
        self._cards.clear()
        self._offer_data.clear()

        if not offers:
            empty = ctk.CTkLabel(
                self,
                text="Nenhuma oferta encontrada.\nClique em 'Nova Oferta' para cadastrar.",
                text_color="#999999",
                justify="center",
            )
            empty.pack(expand=True, fill="both", pady=40)
            return

        for offer in offers:
            card = self._create_card(offer, originals_dir)
            self._cards[offer.id] = card
            self._offer_data[offer.id] = offer

    def _create_card(self, offer: Offer, originals_dir: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(self, corner_radius=8)
        card.pack(fill="x", padx=8, pady=4)

        # Container interno
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=8)

        # Miniatura
        thumb_size = 56
        thumb_frame = ctk.CTkFrame(inner, width=thumb_size, height=thumb_size, corner_radius=6)
        thumb_frame.pack(side="left", padx=(0, 10))
        thumb_frame.pack_propagate(False)

        thumb_label = ctk.CTkLabel(thumb_frame, text="🖼", font=("Segoe UI", 20))
        thumb_label.pack(expand=True, fill="both")

        # Tentar carregar miniatura
        if offer.imagem_original and originals_dir:
            img_path = os.path.join(originals_dir, os.path.basename(offer.imagem_original))
            if os.path.isfile(img_path):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((thumb_size, thumb_size), Image.LANCZOS)
                    from customtkinter import CTkImage
                    ctk_img = CTkImage(light_image=img, dark_image=img, size=(thumb_size, thumb_size))
                    thumb_label.configure(image=ctk_img, text="")
                except Exception:
                    pass

        # Informações
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            info_frame,
            text=offer.titulo,
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        ).pack(fill="x")

        periodo = f"{offer.inicio} → {offer.fim}"
        ctk.CTkLabel(
            info_frame,
            text=periodo,
            font=("Segoe UI", 11),
            text_color="#999999",
            anchor="w",
        ).pack(fill="x")

        # Status e ações
        actions_frame = ctk.CTkFrame(inner, fg_color="transparent")
        actions_frame.pack(side="right", padx=(8, 0))

        # Badge de status
        if offer.is_ativa:
            status_text = "ATIVA"
            status_color = "#4caf50"
        elif offer.is_expirada:
            status_text = "EXPIRADA"
            status_color = "#f44336"
        elif offer.is_pendente:
            status_text = "PENDENTE"
            status_color = "#ff9800"
        else:
            status_text = "INATIVA"
            status_color = "#757575"

        status_badge = ctk.CTkLabel(
            actions_frame,
            text=status_text,
            font=("Segoe UI", 10, "bold"),
            text_color=status_color,
            corner_radius=4,
        )
        status_badge.pack(side="top", padx=2, pady=(0, 4))

        # Botões de ação
        btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        btn_frame.pack(side="bottom")

        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️",
            width=30,
            height=28,
            font=("Segoe UI", 12),
            command=lambda o=offer: self._edit_offer(o),
        )
        edit_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            width=30,
            height=28,
            font=("Segoe UI", 12),
            fg_color="#5c2a2a",
            hover_color="#7a3a3a",
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
