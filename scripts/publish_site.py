"""Script para build + publicação via terminal."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.core.config import AppConfig
from admin.core.paths import find_project_root
from admin.core.git_runner import GitRunner
from admin.models.offer import OfferCollection
from admin.services.image_service import ImageService
from admin.services.site_builder_service import SiteBuilderService
from admin.services.publish_service import PublishService


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

    # Serviços
    image_service = ImageService(config.originals_dir, config.optimized_dir)
    builder = SiteBuilderService(config, image_service)
    git_runner = GitRunner(root, branch=config.publishing.branch)
    publisher = PublishService(builder, git_runner)

    # Verificar ambiente
    warnings = publisher.check_environment()
    if warnings:
        for w in warnings:
            print(f"⚠️  {w}")

    # Publicar
    print("🚀 Publicando site...")
    result = publisher.publish(collection)

    if result.success:
        print(f"✅ {result.output}")
    else:
        print(f"❌ {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
