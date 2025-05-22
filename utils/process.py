import os
import sys
import json
import time
import psutil
import subprocess
from datetime import datetime
from rich.console import Console
from utils.github import find_manifest_file

console = Console()

def run_application(version):
    """Executar a aplicação Java para a versão especificada."""
    # Obter o diretório de instalação
    install_dir = os.path.expanduser(f"~/.fg/installed/{version}")
    if not os.path.exists(install_dir):
        console.print(f"[bold red]Versão {version} não está instalada.[/]")
        return None
    
    # Procurar o manifesto recursivamente
    manifest_path = find_manifest_file(install_dir)
    if not manifest_path:
        console.print(f"[bold red]Arquivo fgmanifest.json não encontrado para a versão {version}.[/]")
        return None
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Obter o caminho do JDK
        from utils.jdk import get_java_path
        jdk_dir = os.path.expanduser(f"~/.fg/jdk/jdk-{manifest['jdk']['version']}")
        if not os.path.exists(jdk_dir):
            console.print(f"[bold red]JDK {manifest['jdk']['version']} não está instalado.[/]")
            return None
        
        java_path = get_java_path(jdk_dir)
        if not os.path.exists(java_path):
            console.print(f"[bold red]Executável Java não encontrado em {java_path}[/]")
            return None
        
        # Preparar o comando para executar a aplicação
        run_command = manifest["runCommand"]
        
        # Substituir 'java' pelo caminho completo do java
        run_command = run_command.replace("java ", f"{java_path} ")
        
        # Criar diretório de logs se não existir
        logs_dir = os.path.expanduser("~/.fg/logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Arquivos de log
        log_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stdout_log = os.path.join(logs_dir, f"{version}_{log_timestamp}.log")
        stderr_log = os.path.join(logs_dir, f"{version}_{log_timestamp}.err")
        
        # Executar a aplicação
        console.print(f"Iniciando aplicação versão {version}...")
        
        # Obter o diretório onde está o JAR (o mesmo diretório do manifesto)
        jar_dir = os.path.dirname(manifest_path)
        
        # Substituir o diretório de trabalho
        os.chdir(jar_dir)
        
        # Executar o processo em background
        with open(stdout_log, 'w') as out, open(stderr_log, 'w') as err:
            process = subprocess.Popen(
                run_command,
                shell=True,
                stdout=out,
                stderr=err,
                text=True
            )
        
        # Registrar o processo
        pid = process.pid
        register_process(version, pid, stdout_log, stderr_log)
        
        console.print(f"[bold green]Aplicação iniciada com sucesso. PID: {pid}[/]")
        return pid
    except Exception as e:
        console.print(f"[bold red]Erro ao executar a aplicação:[/] {str(e)}")
        return None

def register_process(version, pid, stdout_log, stderr_log):
    """Registrar um processo em execução."""
    processes_file = os.path.expanduser("~/.fg/processes.json")
    
    # Carregar processos existentes
    processes = {}
    if os.path.exists(processes_file):
        try:
            with open(processes_file, 'r') as f:
                processes = json.load(f)
        except:
            processes = {}
    
    # Adicionar novo processo
    processes[str(pid)] = {
        "version": version,
        "start_time": time.time(),
        "stdout_log": stdout_log,
        "stderr_log": stderr_log
    }
    
    # Salvar arquivo de processos
    with open(processes_file, 'w') as f:
        json.dump(processes, f, indent=2)

def unregister_process(pid):
    """Remover um processo do registro."""
    processes_file = os.path.expanduser("~/.fg/processes.json")
    
    # Carregar processos existentes
    if not os.path.exists(processes_file):
        return
    
    try:
        with open(processes_file, 'r') as f:
            processes = json.load(f)
        
        # Remover processo
        if str(pid) in processes:
            del processes[str(pid)]
        
        # Salvar arquivo de processos
        with open(processes_file, 'w') as f:
            json.dump(processes, f, indent=2)
    except Exception as e:
        console.print(f"[bold red]Erro ao desregistrar processo {pid}:[/] {str(e)}")

def get_running_processes():
    """Obter todos os processos em execução."""
    processes_file = os.path.expanduser("~/.fg/processes.json")
    
    if not os.path.exists(processes_file):
        return {}
    
    try:
        with open(processes_file, 'r') as f:
            processes = json.load(f)
        
        # Verificar se os processos ainda estão em execução
        running_processes = {}
        for pid, info in processes.items():
            try:
                process = psutil.Process(int(pid))
                if process.is_running():
                    running_processes[pid] = info
                else:
                    # Processo não está mais em execução
                    unregister_process(int(pid))
            except:
                # Processo não existe mais
                unregister_process(int(pid))
        
        return running_processes
    except Exception as e:
        console.print(f"[bold red]Erro ao obter processos em execução:[/] {str(e)}")
        return {}

def stop_process(pid):
    """Parar um processo em execução."""
    try:
        process = psutil.Process(int(pid))
        if process.is_running():
            process.terminate()
            # Esperar um pouco para o processo finalizar
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Se não finalizar no timeout, mata forçadamente
                process.kill()
            
            unregister_process(int(pid))
            console.print(f"[bold green]Instância da aplicação (PID: {pid}) parada com sucesso[/]")
            return True
        else:
            console.print(f"[bold yellow]Processo {pid} não está em execução.[/]")
            unregister_process(int(pid))
            return False
    except psutil.NoSuchProcess:
        console.print(f"[bold yellow]Processo {pid} não existe.[/]")
        unregister_process(int(pid))
        return False
    except Exception as e:
        console.print(f"[bold red]Erro ao parar processo {pid}:[/] {str(e)}")
        return False