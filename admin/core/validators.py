"""Validação de dados de ofertas."""

import re
from datetime import date, datetime
from typing import Optional


class ValidationError(Exception):
    """Erro de validação com mensagem para o usuário."""
    pass


def validar_titulo(titulo: str) -> Optional[str]:
    """Valida o título da oferta. Retorna mensagem de erro ou None."""
    if not titulo or not titulo.strip():
        return "O título é obrigatório."
    if len(titulo.strip()) < 3:
        return "O título deve ter pelo menos 3 caracteres."
    if len(titulo.strip()) > 120:
        return "O título deve ter no máximo 120 caracteres."
    return None


def validar_data(data_str: str, campo: str) -> Optional[str]:
    """Valida uma data em formato ISO (YYYY-MM-DD). Retorna mensagem de erro ou None."""
    if not data_str or not data_str.strip():
        return f"{campo} é obrigatório."
    try:
        date.fromisoformat(data_str.strip())
    except ValueError:
        return f"{campo} deve estar no formato AAAA-MM-DD."
    return None


def validar_periodo(inicio: str, fim: str) -> Optional[str]:
    """Valida se o período (início e fim) é coerente."""
    try:
        d_inicio = date.fromisoformat(inicio)
        d_fim = date.fromisoformat(fim)
    except (ValueError, TypeError):
        return None  # Erro já capturado nas validações individuais

    if d_fim < d_inicio:
        return "A data final não pode ser anterior à data inicial."
    return None


def validar_imagem(filepath: Optional[str]) -> Optional[str]:
    """Valida o arquivo de imagem. Retorna mensagem de erro ou None."""
    if not filepath:
        return "A imagem é obrigatória."
    if not os.path.isfile(filepath):
        return "Arquivo de imagem não encontrado."
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        return "Formato de imagem não suportado. Use JPG, PNG ou WebP."
    return None


def gerar_slug(titulo: str) -> str:
    """Gera um slug a partir do título."""
    slug = titulo.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def gerar_id(data_ref: Optional[date] = None) -> str:
    """Gera um ID único baseado na data e numeração."""
    hoje = data_ref or date.today()
    from datetime import datetime
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{hoje.isoformat()}-{timestamp}"


import os  # noqa: E402 (importado aqui para evitar circularidade)
