"""Testes para o modelo Offer e OfferCollection."""

import sys
import os
import json
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.models.offer import Offer, OfferCollection


# --- Dados de exemplo ---

HOJE = date.today()
ONTEM = (HOJE - timedelta(days=1)).isoformat()
AMANHA = (HOJE + timedelta(days=1)).isoformat()
SEMANA_PASSADA = (HOJE - timedelta(days=8)).isoformat()
SEMANA_QUE_VEM = (HOJE + timedelta(days=8)).isoformat()


def oferta_exemplo(**kwargs) -> Offer:
    defaults = {
        "id": "test-001",
        "slug": "produto-teste",
        "titulo": "Produto Teste",
        "imagem_original": "ofertas/originals/test.jpg",
        "imagem_publica": "ofertas/test.webp",
        "inicio": ONTEM,
        "fim": AMANHA,
        "ativo": True,
        "ordem": 1,
        "criado_em": "2026-07-21T10:00:00",
        "atualizado_em": "2026-07-21T10:00:00",
    }
    defaults.update(kwargs)
    return Offer(**defaults)


# --- Testes de Propriedades ---

def test_oferta_ativa():
    o = oferta_exemplo()
    assert o.is_ativa, "Oferta dentro do período deve estar ativa"


def test_oferta_expirada():
    o = oferta_exemplo(fim=SEMANA_PASSADA)
    assert o.is_expirada, "Oferta com fim no passado deve estar expirada"
    assert not o.is_ativa, "Oferta expirada não deve estar ativa"


def test_oferta_pendente():
    o = oferta_exemplo(inicio=SEMANA_QUE_VEM, fim=SEMANA_QUE_VEM)
    assert o.is_pendente, "Oferta com início futuro deve estar pendente"
    assert not o.is_ativa, "Oferta pendente não deve estar ativa"


def test_oferta_inativa():
    o = oferta_exemplo(ativo=False)
    assert not o.is_ativa, "Oferta inativa não deve estar ativa"


def test_oferta_expirada_por_data():
    """Oferta que vence hoje ainda deve estar ativa."""
    o = oferta_exemplo(fim=HOJE.isoformat())
    assert o.is_ativa, "Oferta que vence hoje deve estar ativa"


# --- Testes de Collection ---

def test_collection_active_filter():
    collection = OfferCollection([
        oferta_exemplo(id="1"),  # ativa
        oferta_exemplo(id="2", fim=SEMANA_PASSADA),  # expirada
        oferta_exemplo(id="3", inicio=SEMANA_QUE_VEM, fim=SEMANA_QUE_VEM),  # pendente
        oferta_exemplo(id="4", ativo=False),  # inativa
    ])
    assert len(collection.active()) == 1, "Apenas 1 oferta deve estar ativa"


def test_collection_search():
    collection = OfferCollection([
        oferta_exemplo(id="1", titulo="Arroz"),
        oferta_exemplo(id="2", titulo="Feijão"),
        oferta_exemplo(id="3", titulo="Arroz Integral"),
    ])
    results = collection.search(termo="arroz")
    assert len(results) == 2, "Busca por 'arroz' deve retornar 2 resultados"


def test_collection_order():
    collection = OfferCollection([
        oferta_exemplo(id="1", ordem=3, titulo="C"),
        oferta_exemplo(id="2", ordem=1, titulo="A"),
        oferta_exemplo(id="3", ordem=2, titulo="B"),
    ])
    ativas = collection.active()
    assert ativas[0].ordem == 1, "Deve ordenar por ordem crescente"


def test_collection_crud():
    collection = OfferCollection()
    offer = oferta_exemplo()
    collection.add(offer)
    assert len(collection) == 1

    collection.remove("test-001")
    assert len(collection) == 0


def test_to_public_dict():
    offer = oferta_exemplo()
    pub = offer.to_public_dict()
    assert "titulo" in pub
    assert "slug" in pub
    assert "imagem" in pub
    assert "id" not in pub, "ID não deve estar no dicionário público"


# --- Serialização ---

def test_serialization_roundtrip():
    original = oferta_exemplo()
    json_str = json.dumps(original.to_dict(), ensure_ascii=False)
    loaded = Offer.from_dict(json.loads(json_str))
    assert loaded.id == original.id
    assert loaded.titulo == original.titulo


# --- Execução ---

if __name__ == "__main__":
    test_oferta_ativa()
    test_oferta_expirada()
    test_oferta_pendente()
    test_oferta_inativa()
    test_oferta_expirada_por_data()
    test_collection_active_filter()
    test_collection_search()
    test_collection_order()
    test_collection_crud()
    test_to_public_dict()
    test_serialization_roundtrip()
    print("✅ Todos os testes passaram!")
