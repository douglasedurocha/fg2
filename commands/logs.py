import os
import click
import time
from rich.console import Console
from rich.syntax import Syntax
from utils.process import get_running_processes

console = Console()

@click.command()
@click.argument("pid", required=False, type=int)
@click.option("--tail", type=int, default=50, help="Número de linhas para mostrar")
@click.option("--follow", "-f", is_flag=True, help="Seguir o arquivo de log em tempo real")
def logs(pid, tail, follow):
    """Visualizar logs de uma instância em execução."""
    # Se não for fornecido PID, listar processos e pedir para escolher
    if pid is None:
        running_processes = get_running_processes()
        
        if not running_processes:
            console.print("[bold yellow]Nenhuma instância em execução.[/]")
            return
        
        console.print("Instâncias em execução:")
        for p, info in running_processes.items():
            console.print(f"  PID: {p} - Versão: {info['version']}")
        
        pid_str = click.prompt("Digite o PID da instância", type=str)
        try:
            pid = int(pid_str)
        except ValueError:
            console.print("[bold red]PID inválido.[/]")
            return
    
    # Verificar se o processo existe
    running_processes = get_running_processes()
    if str(pid) not in running_processes:
        console.print(f"[bold red]Nenhuma instância encontrada com PID {pid}.[/]")
        return
    
    # Obter arquivo de log
    log_file = running_processes[str(pid)]["stdout_log"]
    err_file = running_processes[str(pid)]["stderr_log"]
    
    if not os.path.exists(log_file):
        console.print(f"[bold red]Arquivo de log não encontrado: {log_file}[/]")
        return
    
    # Mostrar logs
    console.print(f"[bold]Logs para a instância com PID {pid}:[/]")
    
    if follow:
        # Seguir logs em tempo real
        console.print(f"[bold]Seguindo logs em tempo real (Ctrl+C para sair)...[/]")
        try:
            with open(log_file, 'r') as f:
                # Primeiro, mostrar as últimas linhas
                f.seek(0, os.SEEK_END)
                file_size = f.tell()
                
                # Voltar até encontrar 'tail' linhas ou o início do arquivo
                lines = []
                line_count = 0
                pos = file_size - 1
                
                while pos >= 0 and line_count < tail:
                    f.seek(pos)
                    char = f.read(1)
                    
                    if char == '\n' and pos != file_size - 1:
                        line_count += 1
                        lines.append(f.readline().strip())
                    pos -= 1
                
                # Mostrar linhas em ordem cronológica
                for line in reversed(lines):
                    console.print(line)
                
                # Seguir novas linhas
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if line:
                        console.print(line.strip())
                    else:
                        time.sleep(0.1)
        except KeyboardInterrupt:
            console.print("\n[bold]Interrompido pelo usuário.[/]")
    else:
        # Mostrar as últimas 'tail' linhas
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        if lines:
            last_lines = lines[-tail:]
            for line in last_lines:
                console.print(line.strip())
        else:
            console.print("[italic]Arquivo de log vazio.[/]")
        
        # Verificar se há erros
        if os.path.exists(err_file) and os.path.getsize(err_file) > 0:
            console.print("\n[bold red]Erros encontrados:[/]")
            with open(err_file, 'r') as f:
                err_lines = f.readlines()
                
            if err_lines:
                last_err_lines = err_lines[-tail:]
                for line in last_err_lines:
                    console.print(f"[red]{line.strip()}[/]")
            else:
                console.print("[italic]Arquivo de erro vazio.[/]") 