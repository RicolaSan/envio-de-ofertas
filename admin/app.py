"""Ponto de entrada do painel administrativo de ofertas."""

import sys
import os

# Garantir que a raiz do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin.core.config import AppConfig
from admin.core.paths import find_project_root
from admin.ui.main_window import MainWindow


def main():
    """Inicializa o painel administrativo."""
    root = find_project_root()
    config = AppConfig(root)

    app = MainWindow(config)
    app.mainloop()


if __name__ == "__main__":
    main()
