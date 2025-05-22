import click
from rich.console import Console
from rich.table import Table
from utils.config import get_installed_versions

console = Console()

@click.command()
def list_installed():
    """Listar versões instaladas."""
    console.print("Verificando versões instaladas...")
    versions = get_installed_versions()
    
    if not versions:
        console.print("[bold yellow]Nenhuma versão instalada.[/]")
        return
    
    # Ordenar versões
    versions.sort(key=lambda x: x["version"], reverse=True)
    
    # Criar tabela
    table = Table(title="Versões Instaladas")
    table.add_column("Versão", style="cyan")
    table.add_column("Nome", style="green")
    table.add_column("JDK", style="yellow")
    table.add_column("Localização", style="blue")
    
    for version in versions:
        table.add_row(
            version["version"],
            version["name"],
            version["jdk_version"],
            version["path"]
        )
    
    console.print(table) 