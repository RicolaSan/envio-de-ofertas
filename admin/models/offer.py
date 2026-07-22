"""Modelo de dados da Oferta."""

import json
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, time
from typing import Optional


@dataclass
class Offer:
    """Representa uma oferta de supermercado."""

    id: str = ""
    slug: str = ""
    titulo: str = ""
    imagem_original: str = ""
    imagem_publica: str = ""
    inicio: str = ""
    fim: str = ""
    ativo: bool = True
    ordem: int = 0
    criado_em: str = ""
    atualizado_em: str = ""

    # --- Propriedades derivadas ---

    @property
    def data_inicio(self) -> Optional[date]:
        try:
            return date.fromisoformat(self.inicio)
        except (ValueError, TypeError):
            return None

    @property
    def data_fim(self) -> Optional[date]:
        try:
            return date.fromisoformat(self.fim)
        except (ValueError, TypeError):
            return None

    @property
    def is_expirada(self) -> bool:
        """True se a data de fim já passou."""
        fim = self.data_fim
        return fim is not None and fim < date.today()

    @property
    def is_ativa(self) -> bool:
        """True se está dentro do período de validade e marcada como ativa."""
        hoje = date.today()
        inicio = self.data_inicio
        fim = self.data_fim
        return (
            self.ativo
            and inicio is not None and inicio <= hoje
            and fim is not None and fim >= hoje
        )

    @property
    def is_pendente(self) -> bool:
        """True se a data de início ainda não chegou."""
        inicio = self.data_inicio
        return inicio is not None and inicio > date.today()

    # --- Serialização ---

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Offer":
        return cls(**data)

    def to_public_dict(self) -> dict:
        """Retorna apenas os campos necessários para o site público."""
        return {
            "slug": self.slug,
            "titulo": self.titulo,
            "imagem": self.imagem_publica,
            "ordem": self.ordem,
        }


class OfferCollection:
    """Gerencia uma lista de ofertas."""

    def __init__(self, offers: Optional[list[Offer]] = None):
        self._offers: list[Offer] = offers or []

    # --- Acesso ---

    def all(self) -> list[Offer]:
        return list(self._offers)

    def get_by_id(self, offer_id: str) -> Optional[Offer]:
        for o in self._offers:
            if o.id == offer_id:
                return o
        return None

    def active(self) -> list[Offer]:
        """Retorna ofertas ativas (dentro do período e ativo=True)."""
        return sorted(
            [o for o in self._offers if o.is_ativa],
            key=lambda o: (o.ordem, o.inicio or "", o.criado_em or ""),
        )

    def expiradas(self) -> list[Offer]:
        return [o for o in self._offers if o.is_expirada]

    def pendentes(self) -> list[Offer]:
        return [o for o in self._offers if o.is_pendente]

    # --- CRUD ---

    def add(self, offer: Offer) -> None:
        self._offers.append(offer)

    def update(self, offer: Offer) -> bool:
        for i, o in enumerate(self._offers):
            if o.id == offer.id:
                self._offers[i] = offer
                return True
        return False

    def remove(self, offer_id: str) -> Optional[Offer]:
        for i, o in enumerate(self._offers):
            if o.id == offer_id:
                return self._offers.pop(i)
        return None

    # --- Filtros e ordenação ---

    def search(self, termo: str = "", status: str = "",
               ordenar_por: str = "criado_em", ordem_desc: bool = True) -> list[Offer]:
        resultados = list(self._offers)

        if termo:
            termo = termo.lower()
            resultados = [o for o in resultados if termo in o.titulo.lower()]

        if status == "ativas":
            resultados = [o for o in resultados if o.is_ativa]
        elif status == "expiradas":
            resultados = [o for o in resultados if o.is_expirada]
        elif status == "pendentes":
            resultados = [o for o in resultados if o.is_pendente]
        elif status == "inativas":
            resultados = [o for o in resultados if not o.ativo]

        colunas = {
            "criado_em": "criado_em",
            "inicio": "inicio",
            "fim": "fim",
            "titulo": "titulo",
            "ordem": "ordem",
        }
        chave = colunas.get(ordenar_por, "criado_em")
        resultados.sort(key=lambda o: (getattr(o, chave) or ""), reverse=ordem_desc)
        return resultados

    # --- Serialização ---

    def to_json(self) -> str:
        return json.dumps([o.to_dict() for o in self._offers],
                          ensure_ascii=False, indent=2)

    def to_public_json(self) -> str:
        return json.dumps([o.to_public_dict() for o in self.active()],
                          ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, data: str) -> "OfferCollection":
        items = json.loads(data)
        return cls([Offer.from_dict(item) for item in items])

    def __len__(self) -> int:
        return len(self._offers)

    def __iter__(self):
        return iter(self._offers)
