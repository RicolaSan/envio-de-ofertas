"""Serviço de geração do site estático a partir dos dados mestres."""

import os
import json
import shutil
from datetime import date
from typing import Optional

from admin.models.offer import OfferCollection
from admin.services.image_service import ImageService
from admin.core.config import AppConfig


class SiteBuilderService:
    """Gera os arquivos do site público em site/."""

    def __init__(self, config: AppConfig, image_service: ImageService):
        self.config = config
        self.image_service = image_service
        self._errors: list[str] = []

    @property
    def errors(self) -> list[str]:
        return list(self._errors)

    def build(self, collection: OfferCollection) -> bool:
        """
        Gera todos os artefatos do site público.
        Retorna True se bem-sucedido.
        """
        self._errors.clear()
        hoje = date.today()

        # 1. Filtrar e ordenar ofertas ativas
        ofertas_publicas = collection.active()

        # 2. Otimizar imagens
        for offer in ofertas_publicas:
            origem = os.path.join(self.config.root_dir, offer.imagem_original.replace("/", os.sep))
            if os.path.isfile(origem):
                self.image_service.optimize(origem, offer.slug)
            else:
                self._errors.append(f"Imagem não encontrada: {offer.imagem_original}")

        # 3. Copiar imagens otimizadas para site/ofertas/
        site_ofertas_dir = os.path.join(self.config.site_dir, "ofertas")
        os.makedirs(site_ofertas_dir, exist_ok=True)
        for offer in ofertas_publicas:
            src = os.path.join(self.config.optimized_dir, f"{offer.slug}.webp")
            dst = os.path.join(site_ofertas_dir, f"{offer.slug}.webp")
            if os.path.isfile(src):
                shutil.copy2(src, dst)

        # 4. Gerar ofertas.json (público)
        public_json = json.dumps(
            [o.to_public_dict() for o in ofertas_publicas],
            ensure_ascii=False, indent=2
        )
        with open(os.path.join(self.config.site_dir, "ofertas.json"), "w", encoding="utf-8") as f:
            f.write(public_json)

        # 5. Gerar index.html
        self._render_template("index.template.html", "index.html", {
            "NOME": self.config.site.nome,
            "DESCRICAO": self.config.site.descricao,
            "URL": self.config.site.url,
            "IDIOMA": self.config.site.idioma,
            "COR_PRIMARIA": self.config.site.cor_primaria,
            "COR_FUNDO": self.config.site.cor_fundo,
            "COR_TEXTO": self.config.site.cor_texto,
            "IMAGEM_PADRAO": self.config.site.imagem_padrao,
        })

        # 6. Gerar manifest.webmanifest
        self._render_template("manifest.template.json", "manifest.webmanifest", {
            "NOME": self.config.site.nome,
            "DESCRICAO": self.config.site.descricao,
            "URL": self.config.site.url,
            "COR_FUNDO": self.config.site.cor_fundo,
            "IDIOMA": self.config.site.idioma,
        })

        # 7. Gerar robots.txt
        self._render_template("robots.template.txt", "robots.txt", {
            "URL": self.config.site.url,
        })

        # 8. Gerar sitemap.xml
        self._render_template("sitemap.template.xml", "sitemap.xml", {
            "URL": self.config.site.url,
            "DATA": hoje.isoformat(),
        })

        # 9. Copiar CSS e JS
        self._copy_assets()

        return len(self._errors) == 0

    def _render_template(self, template_name: str, output_name: str, vars: dict) -> None:
        """Renderiza um template substituindo {{VARIAVEIS}} e salva em site/."""
        template_path = os.path.join(self.config.templates_dir, template_name)
        output_path = os.path.join(self.config.site_dir, output_name)

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            for key, value in vars.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        except FileNotFoundError:
            self._errors.append(f"Template não encontrado: {template_name}")

    def _copy_assets(self) -> None:
        """Copia assets (CSS, JS) do diretório src/assets/ para o site/."""
        origem_assets = os.path.join(self.config.root_dir, "src", "assets")
        destino_assets = os.path.join(self.config.site_dir, "assets")

        if not os.path.isdir(origem_assets):
            # Assets não encontrados — não é fatal, apenas avisa
            print(f"⚠️  Assets não encontrados em: {origem_assets}")
            return

        # Copiar CSS
        origem_css = os.path.join(origem_assets, "css")
        destino_css = os.path.join(destino_assets, "css")
        os.makedirs(destino_css, exist_ok=True)
        if os.path.isdir(origem_css):
            for f in os.listdir(origem_css):
                if f.endswith(".css"):
                    shutil.copy2(os.path.join(origem_css, f), os.path.join(destino_css, f))

        # Copiar JS
        origem_js = os.path.join(origem_assets, "js")
        destino_js = os.path.join(destino_assets, "js")
        os.makedirs(destino_js, exist_ok=True)
        if os.path.isdir(origem_js):
            for f in os.listdir(origem_js):
                if f.endswith(".js"):
                    shutil.copy2(os.path.join(origem_js, f), os.path.join(destino_js, f))

        # Diretório de imagens
        destino_img = os.path.join(destino_assets, "img")
        os.makedirs(destino_img, exist_ok=True)

        # Favicon
        favicon_src = os.path.join(self.config.root_dir, "assets", "favicon", "favicon.ico")
        favicon_dst = os.path.join(self.config.site_dir, "favicon.ico")
        if os.path.isfile(favicon_src) and not os.path.isfile(favicon_dst):
            shutil.copy2(favicon_src, favicon_dst)

    def get_summary(self, collection: OfferCollection) -> str:
        """Retorna um resumo do build para exibição no painel."""
        ativas = len(collection.active())
        total = len(collection)
        expiradas = len(collection.expiradas())
        erros = len(self._errors)
        return (f"✅ {ativas} ofertas ativas geradas "
                f"({total} total, {expiradas} expiradas ignoradas)"
                + (f", {erros} erro(s)" if erros else ""))
