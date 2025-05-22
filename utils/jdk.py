import os
import sys
import platform
import requests
import tarfile
import zipfile
import tempfile
import subprocess
import shutil
from rich.console import Console

console = Console()

def get_platform():
    """Determinar o sistema operacional atual."""
    system = platform.system().lower()
    if system == "darwin":
        return "mac"
    elif system == "windows":
        return "windows"
    else:
        return "linux"

def download_and_install_jdk(jdk_info):
    """Baixar e instalar o JDK necessário."""
    system = get_platform()
    download_url = jdk_info["download"][system]
    jdk_version = jdk_info["version"]
    
    # Verificar se o JDK já está instalado
    jdk_dir = os.path.expanduser(f"~/.fg/jdk/jdk-{jdk_version}")
    if os.path.exists(jdk_dir):
        console.print(f"JDK {jdk_version} já está instalado.")
        return jdk_dir
    
    console.print(f"Baixando JDK {jdk_version}...")
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # Criar um arquivo temporário para o download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
            temp_path = temp_file.name
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
        
        # Criar diretório para o JDK
        os.makedirs(jdk_dir, exist_ok=True)
        
        # Extrair o JDK baseado no formato
        console.print(f"Instalando JDK {jdk_version}...")
        if download_url.endswith('.tar.gz'):
            with tarfile.open(temp_path, 'r:gz') as tar:
                # Obter o nome do diretório raiz do tar
                root_dir = tar.getnames()[0].split('/')[0]
                tar.extractall(os.path.dirname(jdk_dir))
                # Renomear diretório extraído se necessário
                extracted_dir = os.path.join(os.path.dirname(jdk_dir), root_dir)
                if extracted_dir != jdk_dir:
                    if os.path.exists(jdk_dir):
                        shutil.rmtree(jdk_dir)
                    shutil.move(extracted_dir, jdk_dir)
        elif download_url.endswith('.zip'):
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                # Obter o nome do diretório raiz do zip
                root_dir = zip_ref.namelist()[0].split('/')[0]
                zip_ref.extractall(os.path.dirname(jdk_dir))
                # Renomear diretório extraído se necessário
                extracted_dir = os.path.join(os.path.dirname(jdk_dir), root_dir)
                if extracted_dir != jdk_dir and os.path.exists(extracted_dir):
                    if os.path.exists(jdk_dir):
                        shutil.rmtree(jdk_dir)
                    shutil.move(extracted_dir, jdk_dir)
        
        # Remover o arquivo temporário
        os.unlink(temp_path)
        
        console.print(f"JDK {jdk_version} instalado com sucesso.")
        return jdk_dir
    except Exception as e:
        console.print(f"[bold red]Erro ao baixar/instalar JDK {jdk_version}:[/] {str(e)}")
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return None

def get_java_path(jdk_dir):
    """Obter o caminho para o executável java."""
    system = get_platform()
    if system == "windows":
        java_path = os.path.join(jdk_dir, "bin", "java.exe")
    else:
        java_path = os.path.join(jdk_dir, "bin", "java")
    
    # Verificar se o arquivo java existe
    if not os.path.exists(java_path):
        # Tentar encontrar o java dentro de algum subdiretório
        for root, dirs, files in os.walk(jdk_dir):
            if system == "windows" and "java.exe" in files:
                return os.path.join(root, "java.exe")
            elif system != "windows" and "java" in files:
                # Verificar se é realmente o executável (não um diretório)
                java_file = os.path.join(root, "java")
                if os.path.isfile(java_file):
                    return java_file
    
    return java_path

def download_dependencies(dependencies, target_dir):
    """Baixar dependências Maven necessárias."""
    os.makedirs(target_dir, exist_ok=True)
    
    for dep in dependencies:
        group_id = dep["groupId"].replace(".", "/")
        artifact_id = dep["artifactId"]
        version = dep["version"]
        
        # Construir URL do Maven Central
        url = f"https://repo1.maven.org/maven2/{group_id}/{artifact_id}/{version}/{artifact_id}-{version}.jar"
        jar_path = os.path.join(target_dir, f"{artifact_id}-{version}.jar")
        
        # Verificar se já existe
        if os.path.exists(jar_path):
            console.print(f"Dependência {artifact_id}-{version} já existe.")
            continue
        
        try:
            console.print(f"Baixando dependência {artifact_id}-{version}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(jar_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            console.print(f"Dependência {artifact_id}-{version} baixada com sucesso.")
        except Exception as e:
            console.print(f"[bold red]Erro ao baixar dependência {artifact_id}-{version}:[/] {str(e)}")
            continue 