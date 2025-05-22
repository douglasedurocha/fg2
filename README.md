# FG - Gerenciador de Aplicação Java

Um gerenciador de linha de comando (CLI) para baixar, configurar e executar diferentes versões de uma aplicação Java.

## Funcionalidades

* Listar versões disponíveis da aplicação Java no GitHub (`fg available`)
* Listar versões instaladas localmente (`fg list`)
* Instalar versões específicas (`fg install <versão>`)
* Instalar a versão mais recente (`fg update`)
* Verificar o status das instâncias em execução (`fg status`)
* Visualizar logs de instâncias (`fg logs [pid]`)
* Parar instâncias em execução (`fg stop [pid]`)
* Desinstalar versões (`fg uninstall <versão>`)
* Iniciar a aplicação (`fg start [versão]`)
* Interface gráfica (`fg gui`)
* Visualizar configuração de uma versão (`fg config <versão>`)

## Requisitos

- Python 3.7+
- Conexão com a Internet para baixar aplicações e JDKs

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Torne o script executável (Linux/Mac):

```bash
chmod +x fg.py
```

4. (Opcional) Crie um link simbólico para facilitar o uso (Linux/Mac):

```bash
sudo ln -s $(pwd)/fg.py /usr/local/bin/fg
```

## Uso

### Verificar versões disponíveis
```bash
./fg.py available
```

### Instalar uma versão específica
```bash
./fg.py install 1.0.0
```

### Listar versões instaladas
```bash
./fg.py list
```

### Iniciar a aplicação
```bash
./fg.py start 1.0.0
```

### Verificar instâncias em execução
```bash
./fg.py status
```

### Visualizar logs
```bash
./fg.py logs 1234
```

### Parar uma instância
```bash
./fg.py stop 1234
```

### Desinstalar uma versão
```bash
./fg.py uninstall 1.0.0
```

### Iniciar a interface gráfica
```bash
./fg.py gui
```

## Diretórios

- `~/.fg/installed` - Versões instaladas
- `~/.fg/jdk` - JDKs instalados
- `~/.fg/logs` - Logs das aplicações

## Compatibilidade

O FG é compatível com Linux, macOS e Windows. 