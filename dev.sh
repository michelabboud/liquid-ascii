#!/usr/bin/env bash
#
# Liquid ASCII Development Script
# ================================
# Production-ready development environment manager using uv
#
# Usage: ./dev.sh [command] [options]
# Run: ./dev.sh help for full usage information

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="liquid-ascii"
VENV_DIR="${SCRIPT_DIR}/.venv"
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"
PID_FILE="${SCRIPT_DIR}/.dev.pid"
LOG_FILE="${SCRIPT_DIR}/.dev.log"
UV_MIN_VERSION="0.1.0"

# Colors for output
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    MAGENTA='\033[0;35m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    NC='\033[0m' # No Color
else
    RED='' GREEN='' YELLOW='' BLUE='' MAGENTA='' CYAN='' BOLD='' NC=''
fi

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

log_step() {
    echo -e "${CYAN}▶${NC} ${BOLD}$1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get OS type
get_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        MINGW*|MSYS*|CYGWIN*) echo "windows";;
        *)          echo "unknown";;
    esac
}

# Install uv if not present
install_uv() {
    log_step "Checking for uv installation"

    if command_exists uv; then
        local uv_version=$(uv --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        log_success "uv is already installed (version: ${uv_version})"
        return 0
    fi

    log_warning "uv is not installed. Installing now..."

    local os=$(get_os)

    if [[ "$os" == "windows" ]]; then
        log_error "Please install uv manually on Windows:"
        log_error "PowerShell: irm https://astral.sh/uv/install.ps1 | iex"
        exit 1
    else
        # Unix-like systems (Linux/macOS)
        if command_exists curl; then
            curl -LsSf https://astral.sh/uv/install.sh | sh
        elif command_exists wget; then
            wget -qO- https://astral.sh/uv/install.sh | sh
        else
            log_error "Neither curl nor wget found. Please install uv manually:"
            log_error "Visit: https://github.com/astral-sh/uv"
            exit 1
        fi
    fi

    # Reload shell environment
    export PATH="$HOME/.cargo/bin:$PATH"

    if command_exists uv; then
        log_success "uv installed successfully"
    else
        log_error "uv installation failed. Please install manually:"
        log_error "Visit: https://github.com/astral-sh/uv"
        exit 1
    fi
}

# Create virtual environment if it doesn't exist
create_venv() {
    log_step "Setting up virtual environment"

    if [[ -d "$VENV_DIR" ]]; then
        log_success "Virtual environment already exists at: $VENV_DIR"
        return 0
    fi

    log_info "Creating virtual environment with uv..."
    uv venv "$VENV_DIR"

    if [[ -d "$VENV_DIR" ]]; then
        log_success "Virtual environment created at: $VENV_DIR"
    else
        log_error "Failed to create virtual environment"
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        log_error "Virtual environment not found. Run: ./dev.sh setup"
        exit 1
    fi

    # Source the activation script
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate"
        log_success "Virtual environment activated"
    else
        log_error "Activation script not found in: $VENV_DIR/bin/activate"
        exit 1
    fi
}

# Check if requirements are installed
check_requirements() {
    if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
        log_warning "requirements.txt not found"
        return 1
    fi

    # Check if main packages are installed
    if ! python -c "import blessed, numpy, edge_tts, sounddevice, scipy" 2>/dev/null; then
        return 1
    fi

    return 0
}

# Install requirements
install_requirements() {
    log_step "Installing dependencies"

    if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
        log_error "requirements.txt not found at: $REQUIREMENTS_FILE"
        exit 1
    fi

    activate_venv

    log_info "Installing packages with uv pip..."
    uv pip install -r "$REQUIREMENTS_FILE"

    # Install package in editable mode
    if [[ -f "${SCRIPT_DIR}/pyproject.toml" ]]; then
        log_info "Installing package in editable mode..."
        uv pip install -e "$SCRIPT_DIR"
    fi

    log_success "Dependencies installed successfully"
}

# Update/upgrade requirements
update_requirements() {
    log_step "Updating dependencies"

    activate_venv

    log_info "Upgrading packages with uv pip..."
    uv pip install --upgrade -r "$REQUIREMENTS_FILE"

    # Upgrade package in editable mode
    if [[ -f "${SCRIPT_DIR}/pyproject.toml" ]]; then
        uv pip install --upgrade -e "$SCRIPT_DIR"
    fi

    log_success "Dependencies updated successfully"
}

# Run the project
run_project() {
    log_step "Starting Liquid ASCII"

    activate_venv

    # Check if requirements are installed
    if ! check_requirements; then
        log_warning "Dependencies not installed. Installing now..."
        install_requirements
    fi

    # Run with provided arguments
    cd "$SCRIPT_DIR"

    if [[ $# -eq 0 ]]; then
        # Default demo mode
        log_info "Running in demo mode (use --help to see options)"
        python -m src.main
    else
        # Pass all arguments to main
        python -m src.main "$@"
    fi
}

# Run in background
run_background() {
    log_step "Starting Liquid ASCII in background"

    # Check if already running
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log_warning "Process already running with PID: $pid"
            return 0
        else
            log_warning "Stale PID file found. Removing..."
            rm -f "$PID_FILE"
        fi
    fi

    activate_venv

    # Run in background and capture PID
    cd "$SCRIPT_DIR"
    nohup python -m src.main "$@" > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"

    log_success "Process started with PID: $pid"
    log_info "Logs available at: $LOG_FILE"
}

# Stop the project
stop_project() {
    log_step "Stopping Liquid ASCII"

    if [[ ! -f "$PID_FILE" ]]; then
        log_warning "No PID file found. Process may not be running."
        return 0
    fi

    local pid=$(cat "$PID_FILE")

    if ! ps -p "$pid" > /dev/null 2>&1; then
        log_warning "Process not running (PID: $pid)"
        rm -f "$PID_FILE"
        return 0
    fi

    log_info "Stopping process (PID: $pid)..."
    kill "$pid" 2>/dev/null || true

    # Wait for process to stop
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [[ $count -lt 10 ]]; do
        sleep 0.5
        count=$((count + 1))
    done

    if ps -p "$pid" > /dev/null 2>&1; then
        log_warning "Process did not stop gracefully. Force killing..."
        kill -9 "$pid" 2>/dev/null || true
    fi

    rm -f "$PID_FILE"
    log_success "Process stopped"
}

# Check status
status_project() {
    log_step "Checking status"

    echo ""
    echo "Environment Status:"
    echo "===================="

    # Check uv
    if command_exists uv; then
        local uv_version=$(uv --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        echo -e "uv:           ${GREEN}✓${NC} installed (${uv_version})"
    else
        echo -e "uv:           ${RED}✗${NC} not installed"
    fi

    # Check venv
    if [[ -d "$VENV_DIR" ]]; then
        echo -e "venv:         ${GREEN}✓${NC} exists"
    else
        echo -e "venv:         ${RED}✗${NC} not found"
    fi

    # Check requirements
    if [[ -d "$VENV_DIR" ]]; then
        activate_venv
        if check_requirements; then
            echo -e "dependencies: ${GREEN}✓${NC} installed"
        else
            echo -e "dependencies: ${YELLOW}⚠${NC} missing or incomplete"
        fi
    else
        echo -e "dependencies: ${YELLOW}-${NC} venv not found"
    fi

    # Check running process
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "process:      ${GREEN}✓${NC} running (PID: $pid)"
        else
            echo -e "process:      ${RED}✗${NC} not running (stale PID)"
        fi
    else
        echo -e "process:      ${YELLOW}-${NC} not running"
    fi

    echo ""
}

# Full setup (install everything)
full_setup() {
    log_step "Running full setup"
    echo ""

    install_uv
    create_venv
    install_requirements

    echo ""
    log_success "Setup complete! Ready to develop."
    echo ""
    log_info "Quick start:"
    echo "  ./dev.sh run              - Run demo mode"
    echo "  ./dev.sh run --speak \"Hi\" - Speak text"
    echo "  ./dev.sh test             - Run tests"
    echo ""
}

# Run tests
run_tests() {
    log_step "Running tests"

    activate_venv

    # Check if pytest is installed
    if ! python -c "import pytest" 2>/dev/null; then
        log_warning "pytest not installed. Installing dev dependencies..."
        uv pip install -e ".[dev]"
    fi

    cd "$SCRIPT_DIR"

    if [[ $# -eq 0 ]]; then
        pytest
    else
        pytest "$@"
    fi
}

# Clean environment
clean_env() {
    log_step "Cleaning environment"

    # Stop if running
    if [[ -f "$PID_FILE" ]]; then
        stop_project
    fi

    # Remove venv
    if [[ -d "$VENV_DIR" ]]; then
        log_info "Removing virtual environment..."
        rm -rf "$VENV_DIR"
        log_success "Virtual environment removed"
    fi

    # Remove cache files
    log_info "Removing cache files..."
    find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$SCRIPT_DIR" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    rm -f "$PID_FILE" "$LOG_FILE"

    log_success "Environment cleaned"
}

# Show logs
show_logs() {
    if [[ ! -f "$LOG_FILE" ]]; then
        log_warning "No log file found"
        return 0
    fi

    if [[ $# -eq 0 ]]; then
        # Show last 50 lines
        tail -n 50 "$LOG_FILE"
    else
        # Follow logs
        tail -f "$LOG_FILE"
    fi
}

# Print help
print_help() {
    cat << EOF
${BOLD}Liquid ASCII Development Script${NC}
${CYAN}================================${NC}

${BOLD}USAGE:${NC}
    ./dev.sh [command] [options]

${BOLD}COMMANDS:${NC}
    ${GREEN}setup${NC}                   Full setup (install uv, create venv, install deps)
    ${GREEN}install${NC}                 Install dependencies only
    ${GREEN}update${NC}                  Update/upgrade dependencies
    ${GREEN}run${NC} [args]              Run the project (pass args to main.py)
    ${GREEN}start${NC} [args]            Run in background
    ${GREEN}stop${NC}                    Stop background process
    ${GREEN}restart${NC} [args]          Restart background process
    ${GREEN}test${NC} [args]             Run tests (pass args to pytest)
    ${GREEN}status${NC}                  Show environment and process status
    ${GREEN}logs${NC}                    Show recent logs
    ${GREEN}logs -f${NC}                 Follow logs (live)
    ${GREEN}clean${NC}                   Remove venv and cache files
    ${GREEN}shell${NC}                   Activate venv in current shell
    ${GREEN}voices${NC}                  List all English TTS voices
    ${GREEN}help${NC}                    Show this help message

${BOLD}EXAMPLES:${NC}
    # Initial setup
    ./dev.sh setup

    # Run demo mode
    ./dev.sh run

    # Speak text with lip sync
    ./dev.sh run --speak "Hello, world!"

    # Read a file aloud
    ./dev.sh run --tutor README.md

    # With visual effects
    ./dev.sh run --rainbow horizontal --scheme neon

    # Run in background
    ./dev.sh start --speak "Running in background"
    ./dev.sh logs -f

    # Run tests
    ./dev.sh test
    ./dev.sh test tests/test_sdf.py -v

    # Update dependencies
    ./dev.sh update

    # Check status
    ./dev.sh status

${BOLD}ENVIRONMENT:${NC}
    Virtual Environment: ${VENV_DIR}
    Requirements File:   ${REQUIREMENTS_FILE}
    PID File:           ${PID_FILE}
    Log File:           ${LOG_FILE}

${BOLD}MORE INFO:${NC}
    Documentation: See INSTALL.md and README.md
    Project: https://github.com/yourusername/${PROJECT_NAME}

EOF
}

# Activate shell (for interactive use)
activate_shell() {
    if [[ ! -d "$VENV_DIR" ]]; then
        log_error "Virtual environment not found. Run: ./dev.sh setup"
        exit 1
    fi

    log_success "Activating virtual environment..."
    log_info "Run 'deactivate' to exit the virtual environment"
    echo ""

    # This won't work in a subshell, so provide instructions
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        echo "Run this command in your shell:"
        echo -e "  ${CYAN}source ${VENV_DIR}/bin/activate${NC}"
        echo ""
    fi
}

# Main command dispatcher
main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        setup)
            full_setup
            ;;
        install)
            install_uv
            create_venv
            install_requirements
            ;;
        update|upgrade)
            update_requirements
            ;;
        run)
            run_project "$@"
            ;;
        start)
            run_background "$@"
            ;;
        stop)
            stop_project
            ;;
        restart)
            stop_project
            sleep 1
            run_background "$@"
            ;;
        test|tests)
            run_tests "$@"
            ;;
        status)
            status_project
            ;;
        logs)
            show_logs "$@"
            ;;
        clean)
            clean_env
            ;;
        shell|activate)
            activate_shell
            ;;
        voices)
            log_step "Listing English TTS voices"
            activate_venv
            python scripts/list_english_voices.py
            ;;
        help|--help|-h)
            print_help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            print_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
