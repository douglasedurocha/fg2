import click
import time
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from utils.process import get_running_processes

console = Console()

@click.command()
def status():
    """Verificar status das instâncias em execução."""
    console.print("Verificando instâncias em execução...")
    
    running_processes = get_running_processes()
    
    if not running_processes:
        console.print("[bold yellow]Nenhuma instância em execução.[/]")
        return
    
    # Criar tabela
    table = Table(title="Instâncias em Execução")
    table.add_column("PID", style="cyan")
    table.add_column("Versão", style="green")
    table.add_column("Tempo de Execução", style="yellow")
    table.add_column("Arquivo de Log", style="blue")
    
    current_time = time.time()
    
    for pid, info in running_processes.items():
        # Calcular tempo de execução
        start_time = info["start_time"]
        duration = timedelta(seconds=int(current_time - start_time))
        
        # Formatando duração
        if duration.days > 0:
            duration_str = f"{duration.days}d {duration.seconds // 3600}h {(duration.seconds // 60) % 60}m"
        elif duration.seconds // 3600 > 0:
            duration_str = f"{duration.seconds // 3600}h {(duration.seconds // 60) % 60}m {duration.seconds % 60}s"
        elif (duration.seconds // 60) % 60 > 0:
            duration_str = f"{(duration.seconds // 60) % 60}m {duration.seconds % 60}s"
        else:
            duration_str = f"{duration.seconds}s"
        
        table.add_row(
            pid,
            info["version"],
            duration_str,
            info["stdout_log"]
        )
    
    console.print(table) 