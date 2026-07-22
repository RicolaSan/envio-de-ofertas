"""Serviço de otimização de imagens para o site público."""

import os
from typing import Optional
from PIL import Image


class ImageService:
    """Otimiza imagens para o formato WebP com dimensões padronizadas."""

    MAX_WIDTH = 480
    MAX_HEIGHT = 854
    QUALITY = 80

    def __init__(self, originals_dir: str, optimized_dir: str):
        self.originals_dir = originals_dir
        self.optimized_dir = optimized_dir
        os.makedirs(optimized_dir, exist_ok=True)

    def optimize(self, source_path: str, slug: str) -> Optional[str]:
        """
        Otimiza uma imagem para o formato WebP.
        Retorna o caminho da imagem otimizada ou None em caso de erro.
        """
        try:
            img = Image.open(source_path)
        except Exception as e:
            print(f"Erro ao abrir imagem {source_path}: {e}")
            return None

        # Converter para RGB se necessário
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Redimensionar mantendo proporção
        img.thumbnail((self.MAX_WIDTH, self.MAX_HEIGHT), Image.LANCZOS)

        # Criar nova imagem com fundo escuro (para imagens com transparência)
        bg = Image.new("RGB", (self.MAX_WIDTH, self.MAX_HEIGHT), (26, 26, 26))
        offset = ((self.MAX_WIDTH - img.width) // 2,
                  (self.MAX_HEIGHT - img.height) // 2)
        bg.paste(img, offset)

        # Salvar como WebP
        output_path = os.path.join(self.optimized_dir, f"{slug}.webp")
        bg.save(output_path, "WEBP", quality=self.QUALITY)

        return output_path

    def get_public_path(self, slug: str) -> str:
        """Retorna o caminho público relativo da imagem otimizada."""
        return f"ofertas/{slug}.webp"

    def get_optimized_size(self, slug: str) -> int:
        """Retorna o tamanho em bytes da imagem otimizada."""
        path = os.path.join(self.optimized_dir, f"{slug}.webp")
        try:
            return os.path.getsize(path)
        except OSError:
            return 0
