import os
import click
from rich.console import Console
from rich.progress import Progress
from utils.github import download_version, extract_version
from utils.jdk import download_and_install_jdk, download_dependencies

console = Console()

@click.command()
@click.argument("version")
def install(version):
    """Instalar uma versão específica."""
    # Verificar se a versão já está instalada
    install_dir = os.path.expanduser(f"~/.fg/installed/{version}")
    manifest_path = os.path.join(install_dir, "fgmanifest.json")
    
    if os.path.exists(install_dir) and os.path.exists(manifest_path):
        console.print(f"[bold yellow]Versão {version} já está instalada.[/]")
        return
    
    # Se o diretório existe mas o manifesto não, remover o diretório para reinstalar
    if os.path.exists(install_dir) and not os.path.exists(manifest_path):
        import shutil
        console.print(f"[bold yellow]Instalação anterior incompleta encontrada. Removendo...[/]")
        shutil.rmtree(install_dir)
    
    # Baixar a versão
    zip_path = download_version(version)
    if not zip_path:
        console.print(f"[bold red]Falha ao baixar a versão {version}.[/]")
        return
    
    # Extrair a versão
    console.print(f"Extraindo versão {version}...")
    manifest = extract_version(zip_path, version)
    if not manifest:
        console.print(f"[bold red]Falha ao extrair a versão {version}.[/]")
        return
    
    # Baixar e instalar JDK
    console.print(f"Verificando JDK {manifest['jdk']['version']}...")
    jdk_dir = download_and_install_jdk(manifest["jdk"])
    if not jdk_dir:
        console.print(f"[bold red]Falha ao instalar o JDK para a versão {version}.[/]")
        return
    
    # Baixar dependências, se houver
    if "dependencies" in manifest and manifest["dependencies"]:
        console.print("Verificando dependências...")
        libs_dir = os.path.join(install_dir, "libs")
        download_dependencies(manifest["dependencies"], libs_dir)
    
    console.print(f"[bold green]Versão {version} instalada com sucesso![/]")