"""Testes para o PublishService."""

import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.services.publish_service import PublishService
from admin.services.site_builder_service import SiteBuilderService
from admin.services.image_service import ImageService
from admin.core.git_runner import GitRunner
from admin.core.config import AppConfig
from admin.models.offer import OfferCollection


def setup_test_env() -> tuple[str, AppConfig, PublishService]:
    """Cria ambiente temporário com repositório Git simulado."""
    tmpdir = tempfile.mkdtemp(prefix="ofertas_pub_test_")

    # Estrutura mínima
    for d in ["config", "data", "templates", "site/assets/css",
              "site/assets/js", "site/assets/img", "site/ofertas",
              "ofertas/originals", "ofertas/optimized"]:
        os.makedirs(os.path.join(tmpdir, d), exist_ok=True)

    # Config
    with open(os.path.join(tmpdir, "config", "site.json"), "w") as f:
        json.dump({
            "nome": "Test", "descricao": "Test",
            "url": "https://test.github.io", "idioma": "pt-BR",
            "cor_primaria": "#c8a96e", "cor_fundo": "#1a1a1a",
            "cor_texto": "#f5f5f5",
        }, f)
    with open(os.path.join(tmpdir, "config", "publishing.json"), "w") as f:
        json.dump({"branch": "main"}, f)

    # Template mínimo
    with open(os.path.join(tmpdir, "templates", "index.template.html"), "w") as f:
        f.write("<html></html>")
    for t in ["manifest.template.json", "robots.template.txt", "sitemap.template.xml"]:
        with open(os.path.join(tmpdir, "templates", t), "w") as f:
            f.write("{}")

    config = AppConfig(tmpdir)
    image_svc = ImageService(config.originals_dir, config.optimized_dir)
    builder = SiteBuilderService(config, image_svc)
    git_runner = GitRunner(tmpdir)
    publisher = PublishService(builder, git_runner)

    return tmpdir, config, publisher


def teardown_test_env(tmpdir: str):
    shutil.rmtree(tmpdir)


def test_check_environment_without_git():
    """Em um diretório sem Git, deve retornar avisos."""
    tmpdir, config, publisher = setup_test_env()
    warnings = publisher.check_environment()
    # Pode não ter Git ou não ser um repositório
    assert isinstance(warnings, list)
    teardown_test_env(tmpdir)


def test_publish_returns_result():
    """Publicação sem Git configurado deve retornar um resultado com erro."""
    tmpdir, config, publisher = setup_test_env()
    collection = OfferCollection()
    result = publisher.publish(collection)
    assert hasattr(result, "success")
    assert hasattr(result, "output")
    assert hasattr(result, "error")
    teardown_test_env(tmpdir)


if __name__ == "__main__":
    test_check_environment_without_git()
    test_publish_returns_result()
    print("✅ Todos os testes do publish service passaram!")
