"""Utilitários para resolução de caminhos do projeto."""

import os
from pathlib import Path


def find_project_root() -> str:
    """Encontra a raiz do projeto a partir da localização deste arquivo."""
    current = Path(__file__).resolve()
    # Sobe de: admin/core/paths.py -> admin/core -> admin -> raiz
    return str(current.parents[2])


def ensure_dir(path: str) -> str:
    """Garante que um diretório existe e retorna o caminho."""
    os.makedirs(path, exist_ok=True)
    return path


def list_images(directory: str, extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp")) -> list[str]:
    """Lista arquivos de imagem em um diretório."""
    if not os.path.isdir(directory):
        return []
    return sorted(
        [os.path.join(directory, f) for f in os.listdir(directory)
         if f.lower().endswith(extensions)]
    )
