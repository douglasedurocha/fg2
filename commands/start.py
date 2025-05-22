import click
from rich.console import Console
from utils.config import get_installed_versions, get_version_config
from utils.process import run_application

console = Console()

@click.command()
@click.argument("version", required=False)
def start(version):
    """Iniciar uma instância da aplicação."""
    # Se não for fornecida uma versão, listar versões instaladas e pedir para escolher
    if version is None:
        installed_versions = get_installed_versions()
        
        if not installed_versions:
            console.print("[bold yellow]Nenhuma versão instalada.[/]")
            return
        
        # Ordenar versões
        installed_versions.sort(key=lambda x: x["version"], reverse=True)
        
        console.print("Versões instaladas:")
        for i, v in enumerate(installed_versions, 1):
            console.print(f"  {i}. {v['version']} - {v['name']} (JDK {v['jdk_version']})")
        
        choice = click.prompt("Escolha uma versão para iniciar", type=int, default=1)
        
        if choice < 1 or choice > len(installed_versions):
            console.print("[bold red]Escolha inválida.[/]")
            return
        
        version = installed_versions[choice - 1]["version"]
    
    # Verificar se a versão está instalada
    installed_versions = get_installed_versions()
    installed_version_numbers = [v["version"] for v in installed_versions]
    
    if version not in installed_version_numbers:
        console.print(f"[bold red]Versão {version} não está instalada.[/]")
        return
    
    # Iniciar a aplicação
    run_application(version) 