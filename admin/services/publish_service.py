"""Serviço de publicação automatizada: build + Git."""

from datetime import datetime
from typing import Optional

from admin.models.offer import OfferCollection
from admin.services.site_builder_service import SiteBuilderService
from admin.core.git_runner import GitRunner, GitResult


class PublishService:
    """Orquestra o fluxo de build e publicação."""

    def __init__(self, builder: SiteBuilderService, git_runner: GitRunner):
        self.builder = builder
        self.git = git_runner
        self._last_result: Optional[GitResult] = None

    @property
    def last_result(self) -> Optional[GitResult]:
        return self._last_result

    def publish(self, collection: OfferCollection, commit_message: Optional[str] = None) -> GitResult:
        """
        Executa o pipeline completo: build → Git add → commit → push.
        Retorna o resultado da operação.
        """
        # 1. Build do site
        build_ok = self.builder.build(collection)
        if not build_ok:
            self._last_result = GitResult(
                success=False,
                output="",
                error="Erro na geração do site:\n" + "\n".join(self.builder.errors[:5]),
            )
            return self._last_result

        # 2. Validar Git
        git_check = self.git.check_git_installed()
        if not git_check.success:
            self._last_result = git_check
            return git_check

        repo_check = self.git.check_repo()
        if not repo_check.success:
            self._last_result = GitResult(
                success=False,
                output="",
                error="Diretório não é um repositório Git. Execute 'git init' primeiro.",
            )
            return self._last_result

        # 3. Mensagem de commit
        if not commit_message:
            hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
            commit_message = f"feat: atualizar ofertas - {hoje}"

        # 4. Publicar (add + commit + push)
        result = self.git.publish(commit_message)
        self._last_result = result
        return result

    def check_environment(self) -> list[str]:
        """Verifica se o ambiente está pronto para publicação. Retorna lista de avisos."""
        warnings = []

        git_check = self.git.check_git_installed()
        if not git_check.success:
            warnings.append("Git não encontrado. Instale o Git para publicar.")
        else:
            repo_check = self.git.check_repo()
            if not repo_check.success:
                warnings.append("O diretório não é um repositório Git. Execute 'git init'.")
            else:
                remote_check = self.git.check_remote()
                if not remote_check.success:
                    warnings.append("Nenhum remote 'origin' configurado. Use 'git remote add origin <url>'.")

        return warnings
