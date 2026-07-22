"""Execução de comandos Git a partir do painel administrativo."""

import subprocess
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class GitResult:
    """Resultado de uma operação Git."""
    success: bool
    output: str
    error: str = ""


class GitRunner:
    """Gerencia operações Git no repositório do projeto."""

    def __init__(self, repo_path: str, branch: str = "gh-pages"):
        self.repo_path = repo_path
        self.branch = branch

    def _run(self, *args: str) -> GitResult:
        """Executa um comando Git e retorna o resultado."""
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                return GitResult(success=True, output=result.stdout.strip())
            return GitResult(
                success=False,
                output=result.stdout.strip(),
                error=result.stderr.strip(),
            )
        except subprocess.TimeoutExpired:
            return GitResult(success=False, output="", error="Comando Git excedeu o tempo limite.")
        except FileNotFoundError:
            return GitResult(success=False, output="", error="Git não encontrado. Instale o Git e tente novamente.")

    def check_git_installed(self) -> GitResult:
        """Verifica se o Git está instalado e configurado."""
        return self._run("--version")

    def check_repo(self) -> GitResult:
        """Verifica se o diretório é um repositório Git válido."""
        return self._run("status")

    def check_remote(self) -> GitResult:
        """Verifica se o remote 'origin' está configurado."""
        return self._run("remote", "-v")

    def add_all(self) -> GitResult:
        """Executa git add ."""
        return self._run("add", ".")

    def commit(self, message: str) -> GitResult:
        """Executa git commit com a mensagem fornecida."""
        return self._run("commit", "-m", message)

    def push(self) -> GitResult:
        """Executa git push para o branch configurado."""
        return self._run("push", "origin", self.branch)

    def publish(self, commit_message: str) -> GitResult:
        """Executa o fluxo completo: add, commit, push."""
        add_result = self.add_all()
        if not add_result.success:
            return add_result

        commit_result = self.commit(commit_message)
        if not commit_result.success:
            # Pode ser "nothing to commit" — não é erro de verdade
            if "nothing to commit" in commit_result.error.lower():
                return GitResult(success=True, output="Nada a comitar. Site já está atualizado.")
            return commit_result

        push_result = self.push()
        return push_result
