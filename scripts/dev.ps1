<#
.SYNOPSIS
    Liquid ASCII Development Script

.DESCRIPTION
    Production-ready development environment manager using uv for Windows

.PARAMETER Command
    Command to execute (setup, install, run, test, etc.)

.PARAMETER Arguments
    Additional arguments to pass to the command

.EXAMPLE
    .\scripts\dev.ps1 setup
    .\scripts\dev.ps1 run --speak "Hello"
    .\scripts\dev.ps1 test

.NOTES
    Version: 1.0
    Requires: PowerShell 5.1+
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Command = "help",

    [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$Arguments = @()
)

# Configuration
$Script:ProjectName = "liquid-ascii"
$Script:ScriptRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$Script:VenvDir = Join-Path $Script:ScriptRoot ".venv"
$Script:RequirementsFile = Join-Path $Script:ScriptRoot "requirements.txt"
$Script:PidFile = Join-Path $Script:ScriptRoot ".dev.pid"
$Script:LogFile = Join-Path $Script:ScriptRoot ".dev.log"

# Color output helpers
function Write-ColorOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $false)]
        [ValidateSet('Info', 'Success', 'Warning', 'Error', 'Step')]
        [string]$Type = 'Info'
    )

    $colors = @{
        'Info'    = @{ Symbol = 'ℹ'; Color = 'Cyan' }
        'Success' = @{ Symbol = '✓'; Color = 'Green' }
        'Warning' = @{ Symbol = '⚠'; Color = 'Yellow' }
        'Error'   = @{ Symbol = '✗'; Color = 'Red' }
        'Step'    = @{ Symbol = '▶'; Color = 'Magenta' }
    }

    $config = $colors[$Type]
    Write-Host "$($config.Symbol) " -ForegroundColor $config.Color -NoNewline
    Write-Host $Message
}

function Write-Info { Write-ColorOutput -Message $args[0] -Type 'Info' }
function Write-Success { Write-ColorOutput -Message $args[0] -Type 'Success' }
function Write-Warning { Write-ColorOutput -Message $args[0] -Type 'Warning' }
function Write-Error { Write-ColorOutput -Message $args[0] -Type 'Error' }
function Write-Step { Write-ColorOutput -Message $args[0] -Type 'Step' }

# Check if command exists
function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Install uv if not present
function Install-Uv {
    Write-Step "Checking for uv installation"

    if (Test-CommandExists "uv") {
        try {
            $uvVersion = (uv --version 2>&1 | Select-String -Pattern '\d+\.\d+\.\d+').Matches[0].Value
            Write-Success "uv is already installed (version: $uvVersion)"
            return $true
        }
        catch {
            Write-Warning "uv found but version check failed"
        }
    }

    Write-Warning "uv is not installed. Installing now..."

    try {
        # Download and run the installer
        $installScript = Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing
        Invoke-Expression $installScript.Content

        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        if (Test-CommandExists "uv") {
            Write-Success "uv installed successfully"
            return $true
        }
        else {
            Write-Error "uv installation completed but command not found. Please restart your terminal."
            return $false
        }
    }
    catch {
        Write-Error "Failed to install uv: $_"
        Write-Error "Please install manually from: https://github.com/astral-sh/uv"
        return $false
    }
}

# Create virtual environment
function New-VirtualEnvironment {
    Write-Step "Setting up virtual environment"

    if (Test-Path $Script:VenvDir) {
        Write-Success "Virtual environment already exists at: $Script:VenvDir"
        return $true
    }

    Write-Info "Creating virtual environment with uv..."

    try {
        uv venv $Script:VenvDir
        Write-Success "Virtual environment created at: $Script:VenvDir"
        return $true
    }
    catch {
        Write-Error "Failed to create virtual environment: $_"
        return $false
    }
}

# Activate virtual environment
function Enable-VirtualEnvironment {
    if (-not (Test-Path $Script:VenvDir)) {
        Write-Error "Virtual environment not found. Run: .\scripts\dev.ps1 setup"
        exit 1
    }

    $activateScript = Join-Path $Script:VenvDir "Scripts\Activate.ps1"

    if (Test-Path $activateScript) {
        & $activateScript
        Write-Success "Virtual environment activated"
        return $true
    }
    else {
        Write-Error "Activation script not found: $activateScript"
        return $false
    }
}

# Check if requirements are installed
function Test-RequirementsInstalled {
    if (-not (Test-Path $Script:RequirementsFile)) {
        Write-Warning "requirements.txt not found"
        return $false
    }

    # Try to import main packages
    $pythonCheck = @"
try:
    import blessed, numpy, edge_tts, sounddevice, scipy
    exit(0)
except ImportError:
    exit(1)
"@

    $result = python -c $pythonCheck 2>$null
    return $LASTEXITCODE -eq 0
}

# Install requirements
function Install-Requirements {
    Write-Step "Installing dependencies"

    if (-not (Test-Path $Script:RequirementsFile)) {
        Write-Error "requirements.txt not found at: $Script:RequirementsFile"
        exit 1
    }

    Enable-VirtualEnvironment

    Write-Info "Installing packages with uv pip..."

    try {
        uv pip install -r $Script:RequirementsFile

        # Install package in editable mode
        $pyprojectPath = Join-Path $Script:ScriptRoot "pyproject.toml"
        if (Test-Path $pyprojectPath) {
            Write-Info "Installing package in editable mode..."
            uv pip install -e $Script:ScriptRoot
        }

        Write-Success "Dependencies installed successfully"
        return $true
    }
    catch {
        Write-Error "Failed to install dependencies: $_"
        return $false
    }
}

# Update requirements
function Update-Requirements {
    Write-Step "Updating dependencies"

    Enable-VirtualEnvironment

    Write-Info "Upgrading packages with uv pip..."

    try {
        uv pip install --upgrade -r $Script:RequirementsFile

        # Upgrade package in editable mode
        $pyprojectPath = Join-Path $Script:ScriptRoot "pyproject.toml"
        if (Test-Path $pyprojectPath) {
            uv pip install --upgrade -e $Script:ScriptRoot
        }

        Write-Success "Dependencies updated successfully"
        return $true
    }
    catch {
        Write-Error "Failed to update dependencies: $_"
        return $false
    }
}

# Run the project
function Start-Project {
    param([string[]]$Args)

    Write-Step "Starting Liquid ASCII"

    Enable-VirtualEnvironment

    # Check if requirements are installed
    if (-not (Test-RequirementsInstalled)) {
        Write-Warning "Dependencies not installed. Installing now..."
        Install-Requirements
    }

    Push-Location $Script:ScriptRoot

    try {
        if ($Args.Count -eq 0) {
            Write-Info "Running in demo mode (use --help to see options)"
            python -m src.main
        }
        else {
            python -m src.main $Args
        }
    }
    finally {
        Pop-Location
    }
}

# Run in background
function Start-BackgroundProject {
    param([string[]]$Args)

    Write-Step "Starting Liquid ASCII in background"

    # Check if already running
    if (Test-Path $Script:PidFile) {
        $pid = Get-Content $Script:PidFile
        if (Get-Process -Id $pid -ErrorAction SilentlyContinue) {
            Write-Warning "Process already running with PID: $pid"
            return
        }
        else {
            Write-Warning "Stale PID file found. Removing..."
            Remove-Item $Script:PidFile -Force
        }
    }

    Enable-VirtualEnvironment

    Push-Location $Script:ScriptRoot

    try {
        # Start process in background
        $process = Start-Process -FilePath "python" -ArgumentList "-m", "src.main", $Args `
            -NoNewWindow -PassThru -RedirectStandardOutput $Script:LogFile -RedirectStandardError $Script:LogFile

        $process.Id | Out-File $Script:PidFile -Encoding ASCII

        Write-Success "Process started with PID: $($process.Id)"
        Write-Info "Logs available at: $Script:LogFile"
    }
    catch {
        Write-Error "Failed to start background process: $_"
    }
    finally {
        Pop-Location
    }
}

# Stop the project
function Stop-Project {
    Write-Step "Stopping Liquid ASCII"

    if (-not (Test-Path $Script:PidFile)) {
        Write-Warning "No PID file found. Process may not be running."
        return
    }

    $pid = Get-Content $Script:PidFile

    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue

    if (-not $process) {
        Write-Warning "Process not running (PID: $pid)"
        Remove-Item $Script:PidFile -Force
        return
    }

    Write-Info "Stopping process (PID: $pid)..."

    try {
        Stop-Process -Id $pid -Force
        Start-Sleep -Milliseconds 500

        # Wait for process to stop
        $count = 0
        while ((Get-Process -Id $pid -ErrorAction SilentlyContinue) -and ($count -lt 10)) {
            Start-Sleep -Milliseconds 500
            $count++
        }

        Remove-Item $Script:PidFile -Force
        Write-Success "Process stopped"
    }
    catch {
        Write-Error "Failed to stop process: $_"
    }
}

# Check status
function Show-Status {
    Write-Step "Checking status"
    Write-Host ""
    Write-Host "Environment Status:"
    Write-Host "===================="

    # Check uv
    if (Test-CommandExists "uv") {
        try {
            $uvVersion = (uv --version 2>&1 | Select-String -Pattern '\d+\.\d+\.\d+').Matches[0].Value
            Write-Host "uv:           " -NoNewline
            Write-Host "✓" -ForegroundColor Green -NoNewline
            Write-Host " installed ($uvVersion)"
        }
        catch {
            Write-Host "uv:           " -NoNewline
            Write-Host "?" -ForegroundColor Yellow -NoNewline
            Write-Host " installed (version unknown)"
        }
    }
    else {
        Write-Host "uv:           " -NoNewline
        Write-Host "✗" -ForegroundColor Red -NoNewline
        Write-Host " not installed"
    }

    # Check venv
    if (Test-Path $Script:VenvDir) {
        Write-Host "venv:         " -NoNewline
        Write-Host "✓" -ForegroundColor Green -NoNewline
        Write-Host " exists"
    }
    else {
        Write-Host "venv:         " -NoNewline
        Write-Host "✗" -ForegroundColor Red -NoNewline
        Write-Host " not found"
    }

    # Check requirements
    if (Test-Path $Script:VenvDir) {
        Enable-VirtualEnvironment
        if (Test-RequirementsInstalled) {
            Write-Host "dependencies: " -NoNewline
            Write-Host "✓" -ForegroundColor Green -NoNewline
            Write-Host " installed"
        }
        else {
            Write-Host "dependencies: " -NoNewline
            Write-Host "⚠" -ForegroundColor Yellow -NoNewline
            Write-Host " missing or incomplete"
        }
    }
    else {
        Write-Host "dependencies: " -NoNewline
        Write-Host "-" -ForegroundColor Yellow -NoNewline
        Write-Host " venv not found"
    }

    # Check running process
    if (Test-Path $Script:PidFile) {
        $pid = Get-Content $Script:PidFile
        if (Get-Process -Id $pid -ErrorAction SilentlyContinue) {
            Write-Host "process:      " -NoNewline
            Write-Host "✓" -ForegroundColor Green -NoNewline
            Write-Host " running (PID: $pid)"
        }
        else {
            Write-Host "process:      " -NoNewline
            Write-Host "✗" -ForegroundColor Red -NoNewline
            Write-Host " not running (stale PID)"
        }
    }
    else {
        Write-Host "process:      " -NoNewline
        Write-Host "-" -ForegroundColor Yellow -NoNewline
        Write-Host " not running"
    }

    Write-Host ""
}

# Full setup
function Start-FullSetup {
    Write-Step "Running full setup"
    Write-Host ""

    if (-not (Install-Uv)) { exit 1 }
    if (-not (New-VirtualEnvironment)) { exit 1 }
    if (-not (Install-Requirements)) { exit 1 }

    Write-Host ""
    Write-Success "Setup complete! Ready to develop."
    Write-Host ""
    Write-Info "Quick start:"
    Write-Host "  .\scripts\dev.ps1 run              - Run demo mode"
    Write-Host "  .\scripts\dev.ps1 run --speak `"Hi`" - Speak text"
    Write-Host "  .\scripts\dev.ps1 test             - Run tests"
    Write-Host ""
}

# Run tests
function Start-Tests {
    param([string[]]$Args)

    Write-Step "Running tests"

    Enable-VirtualEnvironment

    # Check if pytest is installed
    $pythonCheck = "import pytest"
    $result = python -c $pythonCheck 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "pytest not installed. Installing dev dependencies..."
        uv pip install -e "$Script:ScriptRoot[dev]"
    }

    Push-Location $Script:ScriptRoot

    try {
        if ($Args.Count -eq 0) {
            pytest
        }
        else {
            pytest $Args
        }
    }
    finally {
        Pop-Location
    }
}

# Clean environment
function Clear-Environment {
    Write-Step "Cleaning environment"

    # Stop if running
    if (Test-Path $Script:PidFile) {
        Stop-Project
    }

    # Remove venv
    if (Test-Path $Script:VenvDir) {
        Write-Info "Removing virtual environment..."
        Remove-Item $Script:VenvDir -Recurse -Force
        Write-Success "Virtual environment removed"
    }

    # Remove cache files
    Write-Info "Removing cache files..."
    Get-ChildItem -Path $Script:ScriptRoot -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Path $Script:ScriptRoot -Recurse -Directory -Filter "*.egg-info" | Remove-Item -Recurse -Force

    if (Test-Path $Script:PidFile) { Remove-Item $Script:PidFile -Force }
    if (Test-Path $Script:LogFile) { Remove-Item $Script:LogFile -Force }

    Write-Success "Environment cleaned"
}

# Show logs
function Show-Logs {
    param([string[]]$Args)

    if (-not (Test-Path $Script:LogFile)) {
        Write-Warning "No log file found"
        return
    }

    if ($Args.Count -eq 0) {
        # Show last 50 lines
        Get-Content $Script:LogFile -Tail 50
    }
    elseif ($Args[0] -eq "-f" -or $Args[0] -eq "--follow") {
        # Follow logs
        Get-Content $Script:LogFile -Wait -Tail 20
    }
    else {
        Get-Content $Script:LogFile -Tail 50
    }
}

# Show help
function Show-Help {
    Write-Host ""
    Write-Host "Liquid ASCII Development Script" -ForegroundColor White
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor White
    Write-Host "    .\scripts\dev.ps1 [command] [options]"
    Write-Host ""
    Write-Host "COMMANDS:" -ForegroundColor White
    Write-Host "    setup                   " -NoNewline -ForegroundColor Green
    Write-Host "Full setup (install uv, create venv, install deps)"
    Write-Host "    install                 " -NoNewline -ForegroundColor Green
    Write-Host "Install dependencies only"
    Write-Host "    update                  " -NoNewline -ForegroundColor Green
    Write-Host "Update/upgrade dependencies"
    Write-Host "    run [args]              " -NoNewline -ForegroundColor Green
    Write-Host "Run the project (pass args to main.py)"
    Write-Host "    start [args]            " -NoNewline -ForegroundColor Green
    Write-Host "Run in background"
    Write-Host "    stop                    " -NoNewline -ForegroundColor Green
    Write-Host "Stop background process"
    Write-Host "    restart [args]          " -NoNewline -ForegroundColor Green
    Write-Host "Restart background process"
    Write-Host "    test [args]             " -NoNewline -ForegroundColor Green
    Write-Host "Run tests (pass args to pytest)"
    Write-Host "    status                  " -NoNewline -ForegroundColor Green
    Write-Host "Show environment and process status"
    Write-Host "    logs                    " -NoNewline -ForegroundColor Green
    Write-Host "Show recent logs"
    Write-Host "    logs -f                 " -NoNewline -ForegroundColor Green
    Write-Host "Follow logs (live)"
    Write-Host "    clean                   " -NoNewline -ForegroundColor Green
    Write-Host "Remove venv and cache files"
    Write-Host "    shell                   " -NoNewline -ForegroundColor Green
    Write-Host "Activate venv in current shell"
    Write-Host "    help                    " -NoNewline -ForegroundColor Green
    Write-Host "Show this help message"
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor White
    Write-Host "    # Initial setup"
    Write-Host "    .\scripts\dev.ps1 setup" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    # Run demo mode"
    Write-Host "    .\scripts\dev.ps1 run" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    # Speak text with lip sync"
    Write-Host "    .\scripts\dev.ps1 run --speak `"Hello, world!`"" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    # Read a file aloud"
    Write-Host "    .\scripts\dev.ps1 run --tutor README.md" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    # Run in background"
    Write-Host "    .\scripts\dev.ps1 start --speak `"Running in background`"" -ForegroundColor Cyan
    Write-Host "    .\scripts\dev.ps1 logs -f" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    # Run tests"
    Write-Host "    .\scripts\dev.ps1 test" -ForegroundColor Cyan
    Write-Host "    .\scripts\dev.ps1 test tests\test_sdf.py -v" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "ENVIRONMENT:" -ForegroundColor White
    Write-Host "    Virtual Environment: $Script:VenvDir"
    Write-Host "    Requirements File:   $Script:RequirementsFile"
    Write-Host "    PID File:           $Script:PidFile"
    Write-Host "    Log File:           $Script:LogFile"
    Write-Host ""
}

# Activate shell
function Enable-Shell {
    if (-not (Test-Path $Script:VenvDir)) {
        Write-Error "Virtual environment not found. Run: .\scripts\dev.ps1 setup"
        exit 1
    }

    $activateScript = Join-Path $Script:VenvDir "Scripts\Activate.ps1"

    if (Test-Path $activateScript) {
        Write-Success "Activating virtual environment..."
        Write-Info "Run 'deactivate' to exit the virtual environment"
        Write-Host ""
        & $activateScript
    }
    else {
        Write-Error "Activation script not found: $activateScript"
    }
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "setup" {
        Start-FullSetup
    }
    "install" {
        Install-Uv
        New-VirtualEnvironment
        Install-Requirements
    }
    { $_ -in "update", "upgrade" } {
        Update-Requirements
    }
    "run" {
        Start-Project -Args $Arguments
    }
    "start" {
        Start-BackgroundProject -Args $Arguments
    }
    "stop" {
        Stop-Project
    }
    "restart" {
        Stop-Project
        Start-Sleep -Seconds 1
        Start-BackgroundProject -Args $Arguments
    }
    { $_ -in "test", "tests" } {
        Start-Tests -Args $Arguments
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs -Args $Arguments
    }
    "clean" {
        Clear-Environment
    }
    { $_ -in "shell", "activate" } {
        Enable-Shell
    }
    { $_ -in "help", "--help", "-h", "?" } {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Command"
        Write-Host ""
        Show-Help
        exit 1
    }
}
