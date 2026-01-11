# Development Scripts

This directory contains platform-specific development scripts for the Liquid ASCII project.

## Contents

- **`dev.ps1`** - PowerShell development script for Windows

## Windows PowerShell Script (dev.ps1)

Production-ready development environment manager for Windows using uv.

### Requirements

- Windows with PowerShell 5.1 or later
- PowerShell execution policy set to allow scripts

### Setup

If you get an execution policy error, run PowerShell as Administrator:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Usage

```powershell
# From project root
.\scripts\dev.ps1 [command] [options]

# Examples
.\scripts\dev.ps1 setup                    # Full setup
.\scripts\dev.ps1 run                      # Run demo
.\scripts\dev.ps1 run --speak "Hello"      # Speak text
.\scripts\dev.ps1 test                     # Run tests
.\scripts\dev.ps1 status                   # Check status
```

### Available Commands

| Command | Description |
|---------|-------------|
| `setup` | Full setup (install uv, create venv, install deps) |
| `install` | Install dependencies only |
| `update` | Update/upgrade dependencies |
| `run [args]` | Run the project (pass args to main.py) |
| `start [args]` | Run in background |
| `stop` | Stop background process |
| `restart [args]` | Restart background process |
| `test [args]` | Run tests (pass args to pytest) |
| `status` | Show environment and process status |
| `logs` | Show recent logs |
| `logs -f` | Follow logs (live) |
| `clean` | Remove venv and cache files |
| `shell` | Activate venv in current shell |
| `help` | Show help message |

### Features

- **Automatic uv installation** - Installs uv if not present
- **Virtual environment management** - Creates and activates .venv
- **Fast dependency installation** - Uses uv for 10-100x faster installs
- **Background process management** - Start/stop/restart with PID tracking
- **Comprehensive logging** - All output captured to log files
- **Status checking** - Verify all components are installed
- **Color output** - Clear, colored console output for easy reading

### Common Tasks

#### First-Time Setup

```powershell
# Clone and setup
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii
.\scripts\dev.ps1 setup
```

#### Running the Application

```powershell
# Demo mode
.\scripts\dev.ps1 run

# Speak text
.\scripts\dev.ps1 run --speak "Hello, I am Liquid ASCII"

# Read file aloud
.\scripts\dev.ps1 run --tutor README.md

# With visual effects
.\scripts\dev.ps1 run --rainbow horizontal --scheme neon
```

#### Development Workflow

```powershell
# Check status
.\scripts\dev.ps1 status

# Run tests
.\scripts\dev.ps1 test

# Run specific test
.\scripts\dev.ps1 test tests\test_sdf.py -v

# Update dependencies
.\scripts\dev.ps1 update

# Clean environment
.\scripts\dev.ps1 clean
```

#### Background Execution

```powershell
# Start in background
.\scripts\dev.ps1 start --speak "Running in background"

# View logs
.\scripts\dev.ps1 logs

# Follow logs live
.\scripts\dev.ps1 logs -f

# Stop process
.\scripts\dev.ps1 stop
```

## Linux/macOS Script (dev.sh)

For Linux and macOS users, use the `dev.sh` script in the project root:

```bash
./dev.sh [command] [options]
```

See the main project README for details.

## Comparison

| Feature | dev.sh (Linux/macOS) | dev.ps1 (Windows) |
|---------|----------------------|-------------------|
| uv auto-install | ✓ | ✓ |
| venv management | ✓ | ✓ |
| Dependency install | ✓ | ✓ |
| Run application | ✓ | ✓ |
| Background mode | ✓ | ✓ |
| Testing | ✓ | ✓ |
| Status checking | ✓ | ✓ |
| Log management | ✓ | ✓ |
| Color output | ✓ | ✓ |

Both scripts provide identical functionality, just adapted for their respective platforms.

## Troubleshooting

### PowerShell Execution Policy Error

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### uv Not Found After Install

Close and reopen PowerShell to refresh the PATH.

### Virtual Environment Issues

```powershell
# Recreate everything
.\scripts\dev.ps1 clean
.\scripts\dev.ps1 setup
```

### Script Won't Run

Ensure you're in the project root directory:

```powershell
cd path\to\liquid-ascii
.\scripts\dev.ps1 help
```

## Contributing

When modifying these scripts:

1. Test on the target platform
2. Maintain feature parity between bash and PowerShell versions
3. Update this README with any new commands
4. Keep error handling comprehensive

## License

These scripts are part of the Liquid ASCII project and follow the same MIT license.
