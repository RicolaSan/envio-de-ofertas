"""Serviço de gerenciamento de ofertas — CRUD e persistência."""

import json
import os
import shutil
from typing import Optional

from admin.models.offer import Offer, OfferCollection
from admin.core.validators import (
    validar_titulo, validar_data, validar_periodo,
    gerar_slug, gerar_id, ValidationError,
)
from admin.core.paths import ensure_dir


class OfferService:
    """Gerencia ofertas com persistência em JSON."""

    def __init__(self, offers_json_path: str, originals_dir: str):
        self.offers_json_path = offers_json_path
        self.originals_dir = ensure_dir(originals_dir)
        self._collection: Optional[OfferCollection] = None

    # --- Persistência ---

    def load(self) -> OfferCollection:
        """Carrega as ofertas do arquivo JSON."""
        try:
            with open(self.offers_json_path, "r", encoding="utf-8") as f:
                data = f.read()
            self._collection = OfferCollection.from_json(data)
        except (FileNotFoundError, json.JSONDecodeError):
            self._collection = OfferCollection()
        return self._collection

    def save(self) -> None:
        """Salva as ofertas no arquivo JSON com backup automático."""
        if self._collection is None:
            return

        # Backup antes de salvar
        if os.path.isfile(self.offers_json_path):
            backup_dir = os.path.join(os.path.dirname(self.offers_json_path), "backups")
            ensure_dir(backup_dir)
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"offers_backup_{ts}.json")
            shutil.copy2(self.offers_json_path, backup_path)

        with open(self.offers_json_path, "w", encoding="utf-8") as f:
            f.write(self._collection.to_json())

    @property
    def collection(self) -> OfferCollection:
        if self._collection is None:
            self.load()
        return self._collection  # type: ignore

    # --- CRUD ---

    def criar(self, titulo: str, imagem_path: str, inicio: str, fim: str,
              ativo: bool = True) -> tuple[Optional[Offer], Optional[str]]:
        """Cria uma nova oferta com validação. Retorna (Offer, erro)."""
        # Validações
        erro = validar_titulo(titulo)
        if erro:
            return None, erro
        erro = validar_data(inicio, "Data de início")
        if erro:
            return None, erro
        erro = validar_data(fim, "Data de fim")
        if erro:
            return None, erro
        erro = validar_periodo(inicio, fim)
        if erro:
            return None, erro

        from datetime import datetime, date
        agora = datetime.now()
        hoje = date.today()
        slug = gerar_slug(titulo)
        offer_id = gerar_id(hoje)

        # Nome da imagem original
        ext = os.path.splitext(imagem_path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"
        nome_arquivo = f"{slug}{ext}"
        destino = os.path.join(self.originals_dir, nome_arquivo)

        # Copiar imagem
        try:
            shutil.copy2(imagem_path, destino)
        except (shutil.SameFileError, OSError):
            # Se já está no diretório, usa o caminho relativo
            if os.path.dirname(os.path.abspath(imagem_path)) == os.path.abspath(self.originals_dir):
                destino = imagem_path
            else:
                return None, f"Erro ao copiar imagem: {imagem_path}"

        ordem = len(self.collection) + 1

        offer = Offer(
            id=offer_id,
            slug=slug,
            titulo=titulo.strip(),
            imagem_original=f"ofertas/originals/{nome_arquivo}",
            imagem_publica=f"ofertas/{slug}.webp",
            inicio=inicio.strip(),
            fim=fim.strip(),
            ativo=ativo,
            ordem=ordem,
            criado_em=agora.isoformat(),
            atualizado_em=agora.isoformat(),
        )

        self.collection.add(offer)
        self.save()
        return offer, None

    def editar(self, offer_id: str, titulo: str, inicio: str, fim: str,
               ativo: bool, imagem_path: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """Edita uma oferta existente. Retorna (sucesso, erro)."""
        offer = self.collection.get_by_id(offer_id)
        if not offer:
            return False, "Oferta não encontrada."

        erro = validar_titulo(titulo)
        if erro:
            return False, erro
        erro = validar_data(inicio, "Data de início")
        if erro:
            return False, erro
        erro = validar_data(fim, "Data de fim")
        if erro:
            return False, erro
        erro = validar_periodo(inicio, fim)
        if erro:
            return False, erro

        from datetime import datetime
        slug = gerar_slug(titulo)

        offer.titulo = titulo.strip()
        offer.slug = slug
        offer.inicio = inicio.strip()
        offer.fim = fim.strip()
        offer.ativo = ativo
        offer.atualizado_em = datetime.now().isoformat()

        # Se nova imagem foi fornecida
        if imagem_path and os.path.isfile(imagem_path):
            ext = os.path.splitext(imagem_path)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                ext = ".jpg"
            nome_arquivo = f"{slug}{ext}"
            destino = os.path.join(self.originals_dir, nome_arquivo)
            try:
                shutil.copy2(imagem_path, destino)
            except shutil.SameFileError:
                pass
            offer.imagem_original = f"ofertas/originals/{nome_arquivo}"
            offer.imagem_publica = f"ofertas/{slug}.webp"

        self.collection.update(offer)
        self.save()
        return True, None

    def excluir(self, offer_id: str, remover_imagem: bool = True) -> bool:
        """Exclui uma oferta e opcionalmente sua imagem original."""
        offer = self.collection.remove(offer_id)
        if not offer:
            return False

        if remover_imagem and offer.imagem_original:
            img_path = os.path.join(
                os.path.dirname(self.offers_json_path),
                "..",
                offer.imagem_original.replace("/", os.sep)
            )
            if os.path.isfile(img_path):
                os.remove(img_path)

        self.save()
        return True

    def get_all(self) -> list[Offer]:
        return self.collection.all()

    def get_by_id(self, offer_id: str) -> Optional[Offer]:
        return self.collection.get_by_id(offer_id)

    def search(self, termo: str = "", status: str = "",
               ordenar_por: str = "criado_em", ordem_desc: bool = True) -> list[Offer]:
        return self.collection.search(termo, status, ordenar_por, ordem_desc)
