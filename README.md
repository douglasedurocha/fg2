# FG - Java Application Manager

A simple CLI tool to manage different versions of a Java application.

## Features

- List available versions from GitHub releases
- Install specific versions
- Update to the latest version
- Start and stop application instances
- Monitor running instances
- View application logs
- Graphical user interface

## Installation

1. Clone this repository
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Make the script executable:
```
chmod +x fg.py
```

## Usage

### List available versions
```
python fg.py available
```

### List installed versions
```
python fg.py list
```

### Install a specific version
```
python fg.py install 1.0.0
```

### Update to the latest version
```
python fg.py update
```

### Show configuration for a specific version
```
python fg.py config 1.0.0
```

### Start an application
```
python fg.py start 1.0.0
```

### Check status of running instances
```
python fg.py status
```

### View logs for a specific instance
```
python fg.py logs <pid> --tail 100
```

### Stop a running instance
```
python fg.py stop <pid>
```

### Uninstall a version
```
python fg.py uninstall 1.0.0
```

### Launch the graphical interface
```
python fg.py gui
```

## File Structure

```
fg/
├── commands/          # CLI commands
├── utils/             # Utility functions
├── fg.py              # Main entry point
├── README.md          # Documentation
└── requirements.txt   # Dependencies
```

## Dependencies

- click: Command line interface creation
- requests: HTTP client for GitHub API
- rich: Terminal formatting and display
- psutil: Process management
- customtkinter: GUI toolkit

## Configuration

The tool stores all data in the `~/.fg` directory:
- `~/.fg/versions/`: Installed versions
- `~/.fg/logs/`: Application logs
- `~/.fg/downloads/`: Downloaded packages 