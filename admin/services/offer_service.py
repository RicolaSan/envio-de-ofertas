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
    """Gerencia ofertas com persistência em JSON e sincronização com docs/."""

    def __init__(self, offers_json_path: str, originals_dir: str,
                 docs_ofertas_dir: str = "", docs_root: str = ""):
        self.offers_json_path = offers_json_path
        self.originals_dir = ensure_dir(originals_dir)
        self.docs_ofertas_dir = docs_ofertas_dir
        self.docs_root = docs_root
        self._collection: Optional[OfferCollection] = None
        self._alteracoes_pendentes = False

    @property
    def alteracoes_pendentes(self) -> bool:
        return self._alteracoes_pendentes

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

        self._alteracoes_pendentes = True

    def sincronizar_docs(self) -> list[str]:
        """
        Sincroniza os arquivos públicos (docs/) com os dados atuais.
        Remove imagens órfãs e regera o JSON público.
        Retorna lista de ações realizadas.
        """
        acoes = []
        if not self.docs_ofertas_dir or not os.path.isdir(self.docs_ofertas_dir):
            return acoes

        ativas = self.collection.active()
        slugs_ativas = {o.slug for o in ativas}

        # 1. Remover imagens órfãs de docs/ofertas/
        if os.path.isdir(self.docs_ofertas_dir):
            for arquivo in os.listdir(self.docs_ofertas_dir):
                if not arquivo.endswith(".webp"):
                    continue
                slug = os.path.splitext(arquivo)[0]
                if slug not in slugs_ativas:
                    caminho = os.path.join(self.docs_ofertas_dir, arquivo)
                    try:
                        os.remove(caminho)
                        acoes.append(f"🧹 Removeu imagem órfã: {arquivo}")
                    except OSError:
                        pass

        # 2. Regenerar docs/ofertas.json
        if self.docs_root:
            docs_json_path = os.path.join(self.docs_root, "ofertas.json")
            dados_publicos = [o.to_public_dict() for o in ativas]
            import json as _json
            with open(docs_json_path, "w", encoding="utf-8") as f:
                _json.dump(dados_publicos, f, ensure_ascii=False, indent=2)
            acoes.append(f"📄 Regenerou ofertas.json ({len(ativas)} ofertas)")

        return acoes

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
        self.sincronizar_docs()
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
        self.sincronizar_docs()
        return True, None

    def excluir(self, offer_id: str, remover_imagem: bool = True) -> bool:
        """Exclui uma oferta, imagem original, imagem pública e sincroniza docs/."""
        offer = self.collection.remove(offer_id)
        if not offer:
            return False

        raiz = os.path.dirname(os.path.dirname(self.offers_json_path))

        # Remove imagem original
        if remover_imagem and offer.imagem_original:
            img_path = os.path.join(raiz, offer.imagem_original.replace("/", os.sep))
            if os.path.isfile(img_path):
                os.remove(img_path)

        # Remove imagem pública de docs/ofertas/
        if offer.slug and self.docs_ofertas_dir:
            img_publica = os.path.join(self.docs_ofertas_dir, f"{offer.slug}.webp")
            if os.path.isfile(img_publica):
                os.remove(img_publica)

        # Remove imagem otimizada
        img_optimized = os.path.join(
            raiz, "ofertas", "optimized", f"{offer.slug}.webp"
        )
        if os.path.isfile(img_optimized):
            os.remove(img_optimized)

        self.save()
        self.sincronizar_docs()
        return True

    def get_all(self) -> list[Offer]:
        return self.collection.all()

    def get_by_id(self, offer_id: str) -> Optional[Offer]:
        return self.collection.get_by_id(offer_id)

    def search(self, termo: str = "", status: str = "",
               ordenar_por: str = "criado_em", ordem_desc: bool = True) -> list[Offer]:
        return self.collection.search(termo, status, ordenar_por, ordem_desc)
