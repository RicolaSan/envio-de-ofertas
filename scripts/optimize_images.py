"""Script para otimizar todas as imagens originais para WebP."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.core.config import AppConfig
from admin.core.paths import find_project_root, list_images
from admin.models.offer import OfferCollection
from admin.services.image_service import ImageService


def main():
    root = find_project_root()
    config = AppConfig(root)
    image_service = ImageService(config.originals_dir, config.optimized_dir)

    # Carregar ofertas para extrair slugs
    try:
        with open(config.offers_json_path, "r", encoding="utf-8") as f:
            collection = OfferCollection.from_json(f.read())
    except FileNotFoundError:
        collection = OfferCollection()

    # Se houver ofertas, otimiza pelos slugs
    slugs_para_otimizar = set()
    if len(collection) > 0:
        for offer in collection:
            origem = os.path.join(config.originals_dir, f"{offer.slug}.jpg")
            if not os.path.isfile(origem):
                origem = os.path.join(config.originals_dir, f"{offer.slug}.png")
            if os.path.isfile(origem):
                result = image_service.optimize(origem, offer.slug)
                if result:
                    size = os.path.getsize(result)
                    print(f"  ✅ {offer.slug}.webp ({size/1024:.1f} KB)")
                    slugs_para_otimizar.add(offer.slug)

    # Também otimiza imagens órfãs
    for img_path in list_images(config.originals_dir):
        nome = os.path.splitext(os.path.basename(img_path))[0]
        if nome not in slugs_para_otimizar:
            result = image_service.optimize(img_path, nome)
            if result:
                size = os.path.getsize(result)
                print(f"  📦 {nome}.webp (órfão) ({size/1024:.1f} KB)")

    print("\n✅ Otimização concluída!")


if __name__ == "__main__":
    main()
