import os
import sys
import threading
import click
import customtkinter as ctk
from rich.console import Console
from utils.config import get_installed_versions
from utils.github import get_available_versions
from utils.process import get_running_processes, stop_process, run_application
from commands.install import install

console = Console()

class FgApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurar janela
        self.title("FG - Gerenciador de Aplicação Java")
        self.geometry("800x600")
        
        # Criar tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Criar abas
        self.tab_installed = self.tabview.add("Instaladas")
        self.tab_available = self.tabview.add("Disponíveis")
        self.tab_running = self.tabview.add("Em Execução")
        
        # Configurar aba de versões instaladas
        self.setup_installed_tab()
        
        # Configurar aba de versões disponíveis
        self.setup_available_tab()
        
        # Configurar aba de instâncias em execução
        self.setup_running_tab()
        
        # Iniciar com a aba de instaladas
        self.tabview.set("Instaladas")
        
        # Carregar dados iniciais
        self.refresh_all()
    
    def setup_installed_tab(self):
        # Frame de controle
        control_frame = ctk.CTkFrame(self.tab_installed)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        refresh_btn = ctk.CTkButton(control_frame, text="Atualizar", command=self.refresh_installed)
        refresh_btn.pack(side="left", padx=10)
        
        # Frame da lista
        list_frame = ctk.CTkFrame(self.tab_installed)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Lista de versões instaladas
        self.installed_listbox = ctk.CTkTextbox(list_frame, height=200)
        self.installed_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de ações
        action_frame = ctk.CTkFrame(self.tab_installed)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        start_btn = ctk.CTkButton(action_frame, text="Iniciar", command=self.start_selected)
        start_btn.pack(side="left", padx=10)
        
        uninstall_btn = ctk.CTkButton(action_frame, text="Desinstalar", command=self.uninstall_selected)
        uninstall_btn.pack(side="left", padx=10)
    
    def setup_available_tab(self):
        # Frame de controle
        control_frame = ctk.CTkFrame(self.tab_available)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        refresh_btn = ctk.CTkButton(control_frame, text="Atualizar", command=self.refresh_available)
        refresh_btn.pack(side="left", padx=10)
        
        # Frame da lista
        list_frame = ctk.CTkFrame(self.tab_available)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Lista de versões disponíveis
        self.available_listbox = ctk.CTkTextbox(list_frame, height=200)
        self.available_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de ações
        action_frame = ctk.CTkFrame(self.tab_available)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        install_btn = ctk.CTkButton(action_frame, text="Instalar", command=self.install_selected)
        install_btn.pack(side="left", padx=10)
    
    def setup_running_tab(self):
        # Frame de controle
        control_frame = ctk.CTkFrame(self.tab_running)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        refresh_btn = ctk.CTkButton(control_frame, text="Atualizar", command=self.refresh_running)
        refresh_btn.pack(side="left", padx=10)
        
        # Frame da lista
        list_frame = ctk.CTkFrame(self.tab_running)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Lista de instâncias em execução
        self.running_listbox = ctk.CTkTextbox(list_frame, height=200)
        self.running_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de ações
        action_frame = ctk.CTkFrame(self.tab_running)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        stop_btn = ctk.CTkButton(action_frame, text="Parar", command=self.stop_selected)
        stop_btn.pack(side="left", padx=10)
        
        logs_btn = ctk.CTkButton(action_frame, text="Ver Logs", command=self.view_logs)
        logs_btn.pack(side="left", padx=10)
    
    def refresh_all(self):
        """Atualizar todas as listas."""
        self.refresh_installed()
        self.refresh_available()
        self.refresh_running()
    
    def refresh_installed(self):
        """Atualizar lista de versões instaladas."""
        self.installed_listbox.delete("0.0", "end")
        self.installed_versions = get_installed_versions()
        
        if not self.installed_versions:
            self.installed_listbox.insert("0.0", "Nenhuma versão instalada.")
            return
        
        # Ordenar versões
        self.installed_versions.sort(key=lambda x: x["version"], reverse=True)
        
        for i, version in enumerate(self.installed_versions, 1):
            self.installed_listbox.insert("end", f"{i}. {version['version']} - {version['name']} (JDK {version['jdk_version']})\n")
    
    def refresh_available(self):
        """Atualizar lista de versões disponíveis."""
        self.available_listbox.delete("0.0", "end")
        self.available_listbox.insert("0.0", "Consultando versões disponíveis...\n")
        
        # Usar uma thread para não bloquear a interface
        def fetch_available():
            self.available_versions = get_available_versions()
            
            # Atualizar na thread principal
            self.after(0, self.update_available_list)
        
        threading.Thread(target=fetch_available, daemon=True).start()
    
    def update_available_list(self):
        """Atualizar a lista de versões disponíveis após busca."""
        self.available_listbox.delete("0.0", "end")
        
        if not self.available_versions:
            self.available_listbox.insert("0.0", "Não foi possível obter as versões disponíveis.")
            return
        
        # Ordenar versões
        self.available_versions.sort(key=lambda x: x["version"], reverse=True)
        
        for i, version in enumerate(self.available_versions, 1):
            self.available_listbox.insert("end", f"{i}. {version['version']} (Publicado em: {version['published_at'].split('T')[0]})\n")
    
    def refresh_running(self):
        """Atualizar lista de instâncias em execução."""
        self.running_listbox.delete("0.0", "end")
        self.running_processes = get_running_processes()
        
        if not self.running_processes:
            self.running_listbox.insert("0.0", "Nenhuma instância em execução.")
            return
        
        for i, (pid, info) in enumerate(self.running_processes.items(), 1):
            self.running_listbox.insert("end", f"{i}. PID: {pid} - Versão: {info['version']}\n")
    
    def get_selected_item(self, text_widget, items):
        """Obter o item selecionado de uma lista."""
        try:
            text = text_widget.get("0.0", "end")
            lines = text.strip().split("\n")
            
            if not lines or "Nenhuma" in lines[0]:
                return None
            
            # Mostrar diálogo de seleção
            dialog = ctk.CTkInputDialog(text="Digite o número do item:", title="Selecionar Item")
            result = dialog.get_input()
            
            if not result:
                return None
            
            try:
                index = int(result) - 1
                if 0 <= index < len(items):
                    return items[index]
                else:
                    self.show_error("Número inválido.")
                    return None
            except ValueError:
                self.show_error("Por favor, digite um número válido.")
                return None
        except Exception as e:
            self.show_error(f"Erro ao selecionar item: {str(e)}")
            return None
    
    def show_error(self, message):
        """Mostrar mensagem de erro."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Erro")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        label = ctk.CTkLabel(dialog, text=message)
        label.pack(pady=20)
        
        button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        button.pack(pady=10)
        
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
    
    def show_info(self, message):
        """Mostrar mensagem informativa."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Informação")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        label = ctk.CTkLabel(dialog, text=message)
        label.pack(pady=20)
        
        button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        button.pack(pady=10)
        
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
    
    def start_selected(self):
        """Iniciar a versão selecionada."""
        selected = self.get_selected_item(self.installed_listbox, self.installed_versions)
        if not selected:
            return
        
        version = selected["version"]
        
        # Executar em uma thread para não bloquear a interface
        def start_app():
            pid = run_application(version)
            if pid:
                # Atualizar lista de instâncias em execução
                self.after(1000, self.refresh_running)
                self.after(0, lambda: self.show_info(f"Aplicação iniciada com sucesso. PID: {pid}"))
        
        threading.Thread(target=start_app, daemon=True).start()
    
    def uninstall_selected(self):
        """Desinstalar a versão selecionada."""
        selected = self.get_selected_item(self.installed_listbox, self.installed_versions)
        if not selected:
            return
        
        version = selected["version"]
        
        # Confirmar desinstalação
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        label = ctk.CTkLabel(dialog, text=f"Tem certeza que deseja desinstalar a versão {version}?")
        label.pack(pady=20)
        
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=10)
        
        confirm_btn = ctk.CTkButton(button_frame, text="Sim", command=lambda: self.confirm_uninstall(dialog, version))
        confirm_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Não", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=10)
        
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
    
    def confirm_uninstall(self, dialog, version):
        """Confirmar e executar a desinstalação."""
        dialog.destroy()
        
        from utils.config import uninstall_version
        result = uninstall_version(version)
        
        if result:
            self.show_info(f"Versão {version} desinstalada com sucesso.")
            self.refresh_installed()
        else:
            self.show_error(f"Falha ao desinstalar versão {version}.")
    
    def install_selected(self):
        """Instalar a versão selecionada."""
        selected = self.get_selected_item(self.available_listbox, self.available_versions)
        if not selected:
            return
        
        version = selected["version"]
        
        # Verificar se já está instalada
        installed_versions = get_installed_versions()
        installed_version_numbers = [v["version"] for v in installed_versions]
        
        if version in installed_version_numbers:
            self.show_info(f"Versão {version} já está instalada.")
            return
        
        # Executar em uma thread para não bloquear a interface
        def install_version():
            # Redirect console output to capture it
            class StreamCapture:
                def __init__(self):
                    self.data = ""
                def write(self, data):
                    self.data += data
                def flush(self):
                    pass
            
            stdout_capture = StreamCapture()
            stderr_capture = StreamCapture()
            
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = stdout_capture, stderr_capture
            
            try:
                install.callback(version)
                # Restaurar stdout/stderr
                sys.stdout, sys.stderr = old_stdout, old_stderr
                
                # Atualizar a lista de versões instaladas
                self.after(0, self.refresh_installed)
                self.after(0, lambda: self.show_info(f"Versão {version} instalada com sucesso."))
            except Exception as e:
                # Restaurar stdout/stderr
                sys.stdout, sys.stderr = old_stdout, old_stderr
                self.after(0, lambda: self.show_error(f"Erro ao instalar versão {version}: {str(e)}"))
        
        self.show_info(f"Iniciando instalação da versão {version}. Isso pode levar algum tempo...")
        threading.Thread(target=install_version, daemon=True).start()
    
    def stop_selected(self):
        """Parar a instância selecionada."""
        if not self.running_processes:
            self.show_error("Nenhuma instância em execução.")
            return
        
        # Converter para lista para indexação
        pids = list(self.running_processes.keys())
        processes = [{"pid": pid, "info": self.running_processes[pid]} for pid in pids]
        
        selected = self.get_selected_item(self.running_listbox, processes)
        if not selected:
            return
        
        pid = selected["pid"]
        
        # Confirmar parada
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        label = ctk.CTkLabel(dialog, text=f"Tem certeza que deseja parar a instância com PID {pid}?")
        label.pack(pady=20)
        
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=10)
        
        confirm_btn = ctk.CTkButton(button_frame, text="Sim", command=lambda: self.confirm_stop(dialog, pid))
        confirm_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Não", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=10)
        
        dialog.transient(self)
        dialog.grab_set()
        self.wait_window(dialog)
    
    def confirm_stop(self, dialog, pid):
        """Confirmar e executar a parada."""
        dialog.destroy()
        
        result = stop_process(int(pid))
        
        if result:
            self.show_info(f"Instância com PID {pid} parada com sucesso.")
            self.refresh_running()
        else:
            self.show_error(f"Falha ao parar instância com PID {pid}.")
    
    def view_logs(self):
        """Ver logs da instância selecionada."""
        if not self.running_processes:
            self.show_error("Nenhuma instância em execução.")
            return
        
        # Converter para lista para indexação
        pids = list(self.running_processes.keys())
        processes = [{"pid": pid, "info": self.running_processes[pid]} for pid in pids]
        
        selected = self.get_selected_item(self.running_listbox, processes)
        if not selected:
            return
        
        pid = selected["pid"]
        log_file = self.running_processes[pid]["stdout_log"]
        
        if not os.path.exists(log_file):
            self.show_error(f"Arquivo de log não encontrado: {log_file}")
            return
        
        # Abrir janela com logs
        log_window = ctk.CTkToplevel(self)
        log_window.title(f"Logs - PID {pid}")
        log_window.geometry("800x600")
        
        # Frame de controle
        control_frame = ctk.CTkFrame(log_window)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        refresh_btn = ctk.CTkButton(control_frame, text="Atualizar", 
                                   command=lambda: self.refresh_logs(log_text, log_file))
        refresh_btn.pack(side="left", padx=10)
        
        close_btn = ctk.CTkButton(control_frame, text="Fechar", command=log_window.destroy)
        close_btn.pack(side="right", padx=10)
        
        # Área de texto para logs
        log_text = ctk.CTkTextbox(log_window, height=500)
        log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Carregar logs iniciais
        self.refresh_logs(log_text, log_file)
        
        log_window.transient(self)
        log_window.grab_set()
    
    def refresh_logs(self, text_widget, log_file):
        """Atualizar conteúdo de logs."""
        text_widget.delete("0.0", "end")
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            if not lines:
                text_widget.insert("0.0", "Arquivo de log vazio.")
                return
            
            # Mostrar as últimas 100 linhas ou todas se houver menos
            last_lines = lines[-100:] if len(lines) > 100 else lines
            for line in last_lines:
                text_widget.insert("end", line)
            
            # Rolar para o final
            text_widget.see("end")
        except Exception as e:
            text_widget.insert("0.0", f"Erro ao ler arquivo de log: {str(e)}")

@click.command()
def gui():
    """Iniciar interface gráfica."""
    app = FgApp()
    app.mainloop() 