"""Testes para o SiteBuilderService."""

import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.models.offer import OfferCollection, Offer
from admin.services.site_builder_service import SiteBuilderService
from admin.services.image_service import ImageService
from admin.core.config import AppConfig


def setup_test_env() -> tuple[str, AppConfig, SiteBuilderService]:
    """Cria um ambiente temporário para testes."""
    tmpdir = tempfile.mkdtemp(prefix="ofertas_test_")

    # Estrutura mínima
    os.makedirs(os.path.join(tmpdir, "config"), exist_ok=True)
    os.makedirs(os.path.join(tmpdir, "data"), exist_ok=True)
    os.makedirs(os.path.join(tmpdir, "templates"), exist_ok=True)
    os.makedirs(os.path.join(tmpdir, "site", "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(tmpdir, "site", "assets", "js"), exist_ok=True)
    os.makedirs(os.path.join(tmpdir, "site", "assets", "img"), exist_ok=True)
    os.makedirs(os.path.join(tmpdir, "site", "ofertas"), exist_ok=True)
    os.makedirs(os.path.join(tmpdir, "ofertas", "originals"), exist_ok=True)
    os.makedirs(os.path.join(tmpdir, "ofertas", "optimized"), exist_ok=True)

    # Config
    with open(os.path.join(tmpdir, "config", "site.json"), "w") as f:
        json.dump({
            "nome": "Test Ofertas",
            "descricao": "Teste",
            "url": "https://test.github.io",
            "idioma": "pt-BR",
            "cor_primaria": "#c8a96e",
            "cor_fundo": "#1a1a1a",
            "cor_texto": "#f5f5f5",
            "imagem_padrao": "assets/img/default.jpg",
        }, f)

    with open(os.path.join(tmpdir, "config", "publishing.json"), "w") as f:
        json.dump({"branch": "gh-pages"}, f)

    # Templates
    for name, content in [
        ("index.template.html", "<html><title>{{NOME}}</title></html>"),
        ("manifest.template.json", '{"name": "{{NOME}}"}'),
        ("robots.template.txt", "Sitemap: {{URL}}/sitemap.xml"),
        ("sitemap.template.xml", "<urlset><url><loc>{{URL}}/</loc></url></urlset>"),
    ]:
        with open(os.path.join(tmpdir, "templates", name), "w") as f:
            f.write(content)

    # Criar uma imagem de teste
    from PIL import Image as PILImage
    img_path = os.path.join(tmpdir, "ofertas", "originals", "arroz.jpg")
    test_img = PILImage.new("RGB", (100, 100), color=(200, 100, 50))
    test_img.save(img_path, "JPEG")

    config = AppConfig(tmpdir)
    image_service = ImageService(config.originals_dir, config.optimized_dir)
    builder = SiteBuilderService(config, image_service)

    return tmpdir, config, builder


def teardown_test_env(tmpdir: str):
    shutil.rmtree(tmpdir)


def test_build_generates_files():
    tmpdir, config, builder = setup_test_env()

    collection = OfferCollection([
        Offer(
            id="test-1", slug="arroz", titulo="Arroz",
            imagem_original="ofertas/originals/arroz.jpg",
            imagem_publica="ofertas/arroz.webp",
            inicio="2026-07-20", fim="2026-07-25",
            ativo=True, ordem=1,
            criado_em="2026-07-21T10:00:00",
            atualizado_em="2026-07-21T10:00:00",
        ),
    ])

    success = builder.build(collection)
    assert success, "Build deve ser bem-sucedido"

    # Verificar arquivos gerados
    assert os.path.isfile(os.path.join(config.site_dir, "index.html"))
    assert os.path.isfile(os.path.join(config.site_dir, "ofertas.json"))
    assert os.path.isfile(os.path.join(config.site_dir, "robots.txt"))
    assert os.path.isfile(os.path.join(config.site_dir, "sitemap.xml"))
    assert os.path.isfile(os.path.join(config.site_dir, "manifest.webmanifest"))

    # Verificar conteúdo do index.html
    with open(os.path.join(config.site_dir, "index.html")) as f:
        content = f.read()
    assert "Test Ofertas" in content

    # Verificar ofertas.json
    with open(os.path.join(config.site_dir, "ofertas.json")) as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["titulo"] == "Arroz"

    teardown_test_env(tmpdir)


def test_build_empty_collection():
    tmpdir, config, builder = setup_test_env()
    collection = OfferCollection()

    success = builder.build(collection)
    assert success

    with open(os.path.join(config.site_dir, "ofertas.json")) as f:
        data = json.load(f)
    assert len(data) == 0

    teardown_test_env(tmpdir)


def test_build_filters_expired():
    tmpdir, config, builder = setup_test_env()

    from datetime import date, timedelta
    hoje = date.today()
    collection = OfferCollection([
        Offer(
            id="active", slug="ativo", titulo="Ativo",
            imagem_original="", imagem_publica="",
            inicio=(hoje - timedelta(days=1)).isoformat(),
            fim=(hoje + timedelta(days=1)).isoformat(),
            ativo=True, ordem=1,
            criado_em="2026-07-21T10:00:00",
            atualizado_em="2026-07-21T10:00:00",
        ),
        Offer(
            id="expired", slug="expirado", titulo="Expirado",
            imagem_original="", imagem_publica="",
            inicio=(hoje - timedelta(days=10)).isoformat(),
            fim=(hoje - timedelta(days=3)).isoformat(),
            ativo=True, ordem=2,
            criado_em="2026-07-21T10:00:00",
            atualizado_em="2026-07-21T10:00:00",
        ),
    ])

    builder.build(collection)
    with open(os.path.join(config.site_dir, "ofertas.json")) as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["slug"] == "ativo"

    teardown_test_env(tmpdir)


if __name__ == "__main__":
    test_build_generates_files()
    test_build_empty_collection()
    test_build_filters_expired()
    print("✅ Todos os testes do site builder passaram!")
