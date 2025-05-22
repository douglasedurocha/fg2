import click
from rich.console import Console
from utils.github import get_available_versions
from utils.config import get_installed_versions
from commands.install import install

console = Console()

@click.command()
def update():
    """Instalar a versão mais recente."""
    console.print("Verificando atualizações...")
    
    # Obter versões disponíveis
    available_versions = get_available_versions()
    if not available_versions:
        console.print("[bold red]Não foi possível obter as versões disponíveis.[/]")
        return
    
    # Obter a versão mais recente
    available_versions.sort(key=lambda x: x["version"], reverse=True)
    latest_version = available_versions[0]["version"]
    
    # Verificar se já está instalada
    installed_versions = get_installed_versions()
    installed_version_numbers = [v["version"] for v in installed_versions]
    
    if latest_version in installed_version_numbers:
        console.print(f"[bold green]A versão mais recente ({latest_version}) já está instalada.[/]")
        return
    
    console.print(f"Nova versão disponível: {latest_version}")
    if click.confirm("Deseja instalar esta versão?", default=True):
        # Instalar a nova versão
        install.callback(latest_version) 