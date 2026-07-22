"""Carregamento e acesso às configurações do sistema."""

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class SiteConfig:
    """Configurações do site público."""
    nome: str = "Ofertas do Mercado"
    descricao: str = "Confira as ofertas do seu mercado favorito"
    url: str = ""
    idioma: str = "pt-BR"
    tema: str = "escuro"
    cor_primaria: str = "#c8a96e"
    cor_fundo: str = "#1a1a1a"
    cor_texto: str = "#f5f5f5"
    imagem_padrao: str = "assets/img/default-offer.jpg"
    autor: str = "Administrador"
    twitter: str = ""

    @classmethod
    def load(cls, path: str) -> "SiteConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class PublishingConfig:
    """Configurações de publicação via Git."""
    remote_url: str = ""
    branch: str = "gh-pages"
    commit_message: str = "feat: atualizar ofertas - {data}"
    auto_commit: bool = True

    @classmethod
    def load(cls, path: str) -> "PublishingConfig":
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except FileNotFoundError:
            return cls()


class AppConfig:
    """Agrega todas as configurações do sistema."""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.site = SiteConfig.load(os.path.join(root_dir, "config", "site.json"))
        self.publishing = PublishingConfig.load(os.path.join(root_dir, "config", "publishing.json"))

    @property
    def data_dir(self) -> str:
        return os.path.join(self.root_dir, "data")

    @property
    def templates_dir(self) -> str:
        return os.path.join(self.root_dir, "templates")

    @property
    def site_dir(self) -> str:
        return os.path.join(self.root_dir, "docs")

    @property
    def offers_dir(self) -> str:
        return os.path.join(self.root_dir, "ofertas")

    @property
    def originals_dir(self) -> str:
        return os.path.join(self.offers_dir, "originals")

    @property
    def optimized_dir(self) -> str:
        return os.path.join(self.offers_dir, "optimized")

    @property
    def offers_json_path(self) -> str:
        return os.path.join(self.data_dir, "offers.json")

    @property
    def generated_json_path(self) -> str:
        return os.path.join(self.data_dir, "generated", "public-offers.json")
