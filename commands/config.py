import click
import json
from rich.console import Console
from rich.panel import Panel
from utils.config import get_version_config

console = Console()

@click.command()
@click.argument("version")
def config(version):
    """Mostrar configuração de uma versão específica."""
    # Obter configuração da versão
    manifest = get_version_config(version)
    
    if not manifest:
        return
    
    # Mostrar informações da versão
    console.print(Panel.fit(
        f"[bold]Nome:[/] {manifest.get('name', 'Desconhecido')}\n"
        f"[bold]Versão:[/] {version}\n"
        f"[bold]Descrição:[/] {manifest.get('description', 'Sem descrição')}\n"
        f"[bold]JDK Requerido:[/] {manifest.get('jdk', {}).get('version', 'Desconhecido')}\n"
        f"[bold]Comando de Execução:[/] {manifest.get('runCommand', 'Desconhecido')}"
    ), title=f"Configuração da Versão {version}")
    
    # Mostrar dependências, se houver
    if "dependencies" in manifest and manifest["dependencies"]:
        console.print("\n[bold]Dependências:[/]")
        for i, dep in enumerate(manifest["dependencies"], 1):
            console.print(f"{i}. {dep.get('groupId', '')}:{dep.get('artifactId', '')}:{dep.get('version', '')}")
    else:
        console.print("\n[bold]Dependências:[/] Nenhuma") 