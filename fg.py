#!/usr/bin/env python3
import os
import click
from rich.console import Console

console = Console()

@click.group()
def cli():
    """
    fg - CLI para gerenciar versões da aplicação Java
    """
    # Criar diretório de configuração se não existir
    os.makedirs(os.path.expanduser("~/.fg"), exist_ok=True)
    os.makedirs(os.path.expanduser("~/.fg/logs"), exist_ok=True)
    os.makedirs(os.path.expanduser("~/.fg/installed"), exist_ok=True)
    os.makedirs(os.path.expanduser("~/.fg/jdk"), exist_ok=True)

# Importar comandos
from commands.available import available
from commands.list import list_installed
from commands.install import install
from commands.update import update
from commands.status import status
from commands.logs import logs
from commands.stop import stop
from commands.uninstall import uninstall
from commands.start import start
from commands.gui import gui
from commands.config import config

# Registrar comandos
cli.add_command(available)
cli.add_command(list_installed, name="list")
cli.add_command(install)
cli.add_command(update)
cli.add_command(status)
cli.add_command(logs)
cli.add_command(stop)
cli.add_command(uninstall)
cli.add_command(start)
cli.add_command(gui)
cli.add_command(config)

if __name__ == "__main__":
    cli() 