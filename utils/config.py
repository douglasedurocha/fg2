import os
import json
from rich.console import Console

console = Console()

def get_installed_versions():
    """Obter todas as versões instaladas."""
    installed_dir = os.path.expanduser("~/.fg/installed")
    if not os.path.exists(installed_dir):
        return []
    
    installed_versions = []
    for version_dir in os.listdir(installed_dir):
        version_path = os.path.join(installed_dir, version_dir)
        if os.path.isdir(version_path):
            manifest_path = os.path.join(version_path, "fgmanifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)
                    
                    installed_versions.append({
                        "version": version_dir,
                        "name": manifest.get("name", "Unknown"),
                        "description": manifest.get("description", ""),
                        "jdk_version": manifest.get("jdk", {}).get("version", "Unknown"),
                        "path": version_path
                    })
                except Exception as e:
                    console.print(f"[bold yellow]Erro ao ler manifesto da versão {version_dir}:[/] {str(e)}")
    
    return installed_versions

def get_version_config(version):
    """Obter a configuração de uma versão específica."""
    version_dir = os.path.expanduser(f"~/.fg/installed/{version}")
    manifest_path = os.path.join(version_dir, "fgmanifest.json")
    
    if not os.path.exists(version_dir):
        console.print(f"[bold red]Versão {version} não está instalada.[/]")
        return None
    
    if not os.path.exists(manifest_path):
        console.print(f"[bold red]Arquivo de manifesto não encontrado para a versão {version}.[/]")
        return None
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        return manifest
    except Exception as e:
        console.print(f"[bold red]Erro ao ler configuração da versão {version}:[/] {str(e)}")
        return None

def uninstall_version(version):
    """Desinstalar uma versão específica."""
    import shutil
    from utils.process import get_running_processes, stop_process
    
    version_dir = os.path.expanduser(f"~/.fg/installed/{version}")
    manifest_path = os.path.join(version_dir, "fgmanifest.json")
    
    if not os.path.exists(version_dir):
        console.print(f"[bold red]Versão {version} não está instalada.[/]")
        return False
    
    # Se o diretório existe mas o manifesto não existe, alertar que a instalação está incompleta
    if not os.path.exists(manifest_path):
        console.print(f"[bold yellow]Instalação incompleta da versão {version} encontrada. Removendo...[/]")
        shutil.rmtree(version_dir)
        return True
    
    # Verificar se há instâncias em execução
    running_processes = get_running_processes()
    for pid, info in running_processes.items():
        if info["version"] == version:
            console.print(f"[bold yellow]Parando instância em execução (PID: {pid})...[/]")
            stop_process(int(pid))
    
    # Remover diretório
    try:
        shutil.rmtree(version_dir)
        console.print(f"[bold green]Versão {version} desinstalada com sucesso.[/]")
        return True
    except Exception as e:
        console.print(f"[bold red]Erro ao desinstalar versão {version}:[/] {str(e)}")
        return False