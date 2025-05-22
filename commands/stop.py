import click
from rich.console import Console
from utils.process import get_running_processes, stop_process

console = Console()

@click.command()
@click.argument("pid", required=False, type=int)
def stop(pid):
    """Parar uma instância em execução."""
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
    
    # Parar o processo
    console.print(f"Parando instância com PID {pid}...")
    stop_process(pid) 