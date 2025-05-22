import click
from rich.console import Console
from utils.config import get_installed_versions, uninstall_version

console = Console()

@click.command()
@click.argument("version")
def uninstall(version):
    """Desinstalar uma versão específica."""
    # Verificar se a versão está instalada
    installed_versions = get_installed_versions()
    installed_version_numbers = [v["version"] for v in installed_versions]
    
    if version not in installed_version_numbers:
        console.print(f"[bold red]Versão {version} não está instalada.[/]")
        return
    
    # Confirmar desinstalação
    if click.confirm(f"Tem certeza que deseja desinstalar a versão {version}?", default=False):
        # Desinstalar versão
        uninstall_version(version) 