"""Utilitários para resolução de caminhos do projeto."""

import os
import sys
from pathlib import Path


def find_project_root() -> str:
    """
    Encontra a raiz do projeto.
    - Em modo script: sobe de admin/core/paths.py -> admin/core -> admin -> raiz
    - Em modo .exe (PyInstaller): usa a pasta onde o .exe está
    """
    if getattr(sys, 'frozen', False):
        # Modo PyInstaller: o .exe está na raiz do projeto
        return str(Path(sys.executable).resolve().parent)
    # Modo script Python
    current = Path(__file__).resolve()
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
