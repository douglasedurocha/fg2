import os
import json
import requests
import zipfile
import tempfile
from rich.console import Console

console = Console()

GITHUB_REPO = "douglasedurocha/java-app"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases"

def get_available_versions():
    """Obter todas as versões disponíveis no GitHub."""
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        releases = response.json()
        
        versions = []
        for release in releases:
            # Extrair a versão do nome da tag (ex: "v1.0.0" -> "1.0.0")
            version = release["tag_name"].lstrip("v")
            versions.append({
                "version": version,
                "published_at": release["published_at"],
                "download_url": f"https://github.com/{GITHUB_REPO}/releases/download/v{version}/java-app-{version}.zip"
            })
        
        return versions
    except requests.RequestException as e:
        console.print(f"[bold red]Erro ao obter versões:[/] {str(e)}")
        return []

def download_version(version):
    """Baixar uma versão específica da aplicação."""
    versions = get_available_versions()
    download_url = None
    
    for v in versions:
        if v["version"] == version:
            download_url = v["download_url"]
            break
    
    if not download_url:
        console.print(f"[bold red]Versão {version} não encontrada[/]")
        return None
    
    try:
        console.print(f"Baixando versão {version}...")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # Criar um arquivo temporário para o download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_path = temp_file.name
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
        
        return temp_path
    except requests.RequestException as e:
        console.print(f"[bold red]Erro ao baixar versão {version}:[/] {str(e)}")
        return None

def find_manifest_file(dir_path):
    """Encontrar o arquivo fgmanifest.json recursivamente."""
    for root, dirs, files in os.walk(dir_path):
        if "fgmanifest.json" in files:
            return os.path.join(root, "fgmanifest.json")
    return None

def extract_version(zip_path, version):
    """Extrair a versão baixada para o diretório de instalação."""
    install_dir = os.path.expanduser(f"~/.fg/installed/{version}")
    os.makedirs(install_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_dir)
        
        # Verificar se o arquivo fgmanifest.json existe (recursivamente)
        manifest_path = find_manifest_file(install_dir)
        if not manifest_path:
            console.print(f"[bold red]Arquivo fgmanifest.json não encontrado na versão {version}[/]")
            return None
        
        # Carregar o manifesto
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Copiar o manifesto para a raiz do diretório de instalação
        import shutil
        root_manifest_path = os.path.join(install_dir, "fgmanifest.json")
        if manifest_path != root_manifest_path:
            shutil.copy(manifest_path, root_manifest_path)
        
        # Remover o arquivo ZIP temporário
        os.unlink(zip_path)
        
        return manifest
    except (zipfile.BadZipFile, json.JSONDecodeError, OSError) as e:
        console.print(f"[bold red]Erro ao extrair versão {version}:[/] {str(e)}")
        return None