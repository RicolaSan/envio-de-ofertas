"""Script para gerar o site público a partir do terminal."""

import sys
import os

# Adiciona a raiz do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.core.config import AppConfig
from admin.core.paths import find_project_root
from admin.models.offer import OfferCollection
from admin.services.image_service import ImageService
from admin.services.site_builder_service import SiteBuilderService


def main():
    root = find_project_root()
    config = AppConfig(root)

    # Carregar ofertas
    try:
        with open(config.offers_json_path, "r", encoding="utf-8") as f:
            collection = OfferCollection.from_json(f.read())
    except FileNotFoundError:
        print("❌ Arquivo de ofertas não encontrado:", config.offers_json_path)
        sys.exit(1)

    # Build
    image_service = ImageService(config.originals_dir, config.optimized_dir)
    builder = SiteBuilderService(config, image_service)
    success = builder.build(collection)

    if success:
        print(builder.get_summary(collection))
        print(f"📁 Site gerado em: {config.site_dir}")
    else:
        print("❌ Erros na geração:")
        for err in builder.errors:
            print(f"  - {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
