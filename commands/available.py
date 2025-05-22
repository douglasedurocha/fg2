import click
from rich.console import Console
from rich.table import Table
from utils.github import get_available_versions

console = Console()

@click.command()
def available():
    """Listar versões disponíveis para instalação."""
    console.print("Consultando versões disponíveis...")
    versions = get_available_versions()
    
    if not versions:
        console.print("[bold yellow]Não foi possível obter as versões disponíveis.[/]")
        return
    
    # Ordenar versões
    versions.sort(key=lambda x: x["version"], reverse=True)
    
    # Criar tabela
    table = Table(title="Versões Disponíveis")
    table.add_column("Versão", style="cyan")
    table.add_column("Data de Publicação", style="green")
    
    for version in versions:
        table.add_row(
            version["version"],
            version["published_at"].split("T")[0]  # Formato simplificado de data
        )
    
    console.print(table) 