#!/bin/bash
#
# Slack Management Platform - Installation Script
# Automated setup for macOS and Linux
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  Slack Management Platform - Installation${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_python() {
    print_info "Checking Python installation..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3 found: $PYTHON_VERSION"

        # Check version is 3.8+
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python version is compatible (3.8+)"
        else
            print_error "Python 3.8+ is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8+"
        print_info "On macOS: brew install python3"
        exit 1
    fi
}

check_pip() {
    print_info "Checking pip installation..."

    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_warning "pip3 not found. Installing..."
        python3 -m ensurepip --upgrade
        print_success "pip3 installed"
    fi
}

install_dependencies() {
    print_info "Installing Python dependencies..."

    if [ -f "requirements.lock" ]; then
        pip3 install -r requirements.lock --quiet
        print_success "Dependencies installed"
    elif [ -f "requirements.txt" ]; then
        print_warning "requirements.lock not found, falling back to requirements.txt"
        pip3 install -r requirements.txt --quiet
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

setup_config() {
    print_info "Setting up configuration..."

    if [ ! -f "config/config.json" ]; then
        if [ -f "config/config.example.json" ]; then
            cp config/config.example.json config/config.json
            print_success "Config file created: config/config.json"
            print_warning "You need to edit config/config.json with your Slack token"
        else
            print_error "config/config.example.json not found"
            exit 1
        fi
    else
        print_info "Config file already exists"
    fi
}

create_directories() {
    print_info "Creating necessary directories..."

    mkdir -p backups
    mkdir -p exports
    mkdir -p logs

    print_success "Directories created"
}

set_permissions() {
    print_info "Setting file permissions..."

    # Make main scripts executable
    chmod +x slack-manager.py 2>/dev/null || true
    chmod +x setup_wizard.py 2>/dev/null || true
    chmod +x install.sh 2>/dev/null || true

    print_success "Permissions set"
}

test_connection() {
    print_info "Testing Slack API connection..."

    # Check if config has been updated
    if grep -q "xoxb-your-bot-token-here" config/config.json; then
        print_warning "Slack token not configured yet"
        print_info "Please edit config/config.json with your token, then run:"
        print_info "  python3 scripts/utils/test_connection.py"
        return
    fi

    # Test connection
    if python3 scripts/utils/test_connection.py &> /dev/null; then
        print_success "Slack API connection successful!"
    else
        print_warning "Could not connect to Slack API"
        print_info "Please verify your token in config/config.json"
        print_info "Then run: python3 scripts/utils/test_connection.py"
    fi
}

show_next_steps() {
    echo ""
    echo -e "${BLUE}================================================${NC}"
    echo -e "${GREEN}✅ Installation Complete!${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Configure your Slack token:"
    echo "   ${YELLOW}nano config/config.json${NC}"
    echo ""
    echo "2. Test your connection:"
    echo "   ${YELLOW}make test${NC}"
    echo "   or: ${YELLOW}python3 scripts/utils/test_connection.py${NC}"
    echo ""
    echo "3. View available commands:"
    echo "   ${YELLOW}make help${NC}"
    echo ""
    echo "4. Get workspace stats:"
    echo "   ${YELLOW}make stats${NC}"
    echo ""
    echo "5. View documentation:"
    echo "   - README.md - Main documentation"
    echo "   - QUICKSTART.md - Quick start guide"
    echo "   - SLACK_API_GUIDE.md - Complete API guide"
    echo "   - examples/EXAMPLES.md - Usage examples"
    echo ""
    echo "Useful commands:"
    echo "   ${YELLOW}make list-users${NC}      - List all users"
    echo "   ${YELLOW}make list-channels${NC}   - List all channels"
    echo "   ${YELLOW}make backup${NC}          - Create backup"
    echo "   ${YELLOW}make stats${NC}           - Show statistics"
    echo ""
    echo -e "${GREEN}Happy Slack managing! 🚀${NC}"
    echo ""
}

# Main installation flow
main() {
    print_header

    # Check prerequisites
    check_python
    check_pip

    # Install
    install_dependencies
    setup_config
    create_directories
    set_permissions

    # Test (if configured)
    test_connection

    # Show next steps
    show_next_steps
}

# Run installation
main
