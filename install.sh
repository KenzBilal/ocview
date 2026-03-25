#!/bin/bash
set -e

REPO_URL="https://github.com/KenzBilal/ocview"
INSTALL_DIR="$HOME/.local/share/ocview"
BIN_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/ocview"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() { echo -e "${BLUE}[ocview]${NC} $1"; }
print_ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
print_err()  { echo -e "${RED}[✗]${NC} $1"; }

# Header
echo ""
echo "  ┌─────────────────────────────┐"
echo "  │   ocview installer v0.1.0   │"
echo "  │  WebView panel for OpenCode │"
echo "  └─────────────────────────────┘"
echo ""

# Step 1 — Detect Linux distro and install WebKitGTK
detect_and_install_deps() {
    print_step "Detecting Linux distribution..."

    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    else
        print_err "Cannot detect distro. Install manually:"
        print_err "WebKitGTK 4.1, Python 3.10+, GTK3"
        exit 1
    fi

    print_ok "Detected: $PRETTY_NAME"
    print_step "Installing system dependencies..."

    case $DISTRO in
        ubuntu|debian|linuxmint|pop)
            sudo apt-get update -qq
            sudo apt-get install -y \
                python3 python3-pip python3-venv python3-gi python3-gi-cairo \
                gir1.2-gtk-3.0 gir1.2-webkit2-4.1 \
                libgirepository1.0-dev gcc libcairo2-dev \
                pkg-config python3-dev gir1.2-glib-2.0 git
            ;;
        fedora)
            sudo dnf install -y \
                python3 python3-pip python3-gobject \
                gtk3 webkit2gtk4.1 python3-cairo \
                gobject-introspection-devel cairo-devel git
            ;;
        arch|manjaro|endeavouros)
            sudo pacman -Sy --noconfirm \
                python python-pip python-gobject \
                gtk3 webkit2gtk-4.1 python-cairo \
                gobject-introspection git
            ;;
        opensuse|opensuse-leap|opensuse-tumbleweed)
            sudo zypper install -y \
                python3 python3-pip python3-gobject \
                gtk3 webkit2gtk4_1 typelib-1_0-WebKit2-4_1 \
                gobject-introspection git
            ;;
        *)
            print_warn "Unknown distro: $DISTRO"
            print_warn "Please install manually:"
            print_warn "- Python 3.10+"
            print_warn "- PyGObject (python3-gi)"
            print_warn "- WebKitGTK 4.1"
            print_warn "- GTK3"
            read -p "Continue anyway? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi
            ;;
    esac
    print_ok "System dependencies installed"
}

# Step 2 — Check Python version
check_python() {
    print_step "Checking Python version..."
    PYTHON=$(which python3)
    PYVER=$($PYTHON --version 2>&1 | cut -d' ' -f2)
    MAJOR=$(echo $PYVER | cut -d'.' -f1)
    MINOR=$(echo $PYVER | cut -d'.' -f2)

    if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]; }; then
        print_err "Python 3.10+ required. Found: $PYVER"
        exit 1
    fi
    print_ok "Python $PYVER found"
}

# Step 3 — Clone or update repo
install_ocview() {
    print_step "Installing ocview..."

    if [ -d "$INSTALL_DIR" ]; then
        print_warn "Existing installation found. Updating..."
        cd "$INSTALL_DIR"
        git pull origin main 2>/dev/null || git pull
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi

    cd "$INSTALL_DIR"

    print_step "Creating virtual environment..."
    python3 -m venv --system-site-packages .venv

    print_step "Installing Python dependencies..."
    .venv/bin/pip install -q --upgrade pip
    .venv/bin/pip install -q -r requirements.txt
    print_ok "Python dependencies installed"
}

# Step 4 — Create bin symlink
setup_bin() {
    print_step "Setting up ocview command..."
    mkdir -p "$BIN_DIR"
    chmod +x "$INSTALL_DIR/ocview"
    ln -sf "$INSTALL_DIR/ocview" "$BIN_DIR/ocview"

    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        if [ -f ~/.bashrc ]; then
            grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc || \
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        fi
        if [ -f ~/.zshrc ]; then
            grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' ~/.zshrc || \
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        fi
        print_warn "Added $BIN_DIR to PATH. Run: source ~/.bashrc"
    fi
    print_ok "ocview command available"
}

# Step 5 — Create config directory
setup_config() {
    print_step "Setting up config directory..."
    mkdir -p "$CONFIG_DIR"
    print_ok "Config directory: $CONFIG_DIR"
}

# Step 6 — Show OpenCode integration instructions
show_opencode_setup() {
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  ocview installed successfully!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "  Add to ~/.config/opencode/opencode.json:"
    echo ""
    echo '  {'
    echo '    "mcp": {'
    echo '      "ocview": {'
    echo '        "type": "local",'
    echo "        \"command\": [\"$BIN_DIR/ocview\", \"--mcp\"],"
    echo '        "enabled": true'
    echo '      }'
    echo '    }'
    echo '  }'
    echo ""
    echo "  Start ocview:"
    echo "    $ ocview"
    echo ""
    echo "  Then in OpenCode chat:"
    echo '    "open localhost:3000"'
    echo '    "describe the current page"'
    echo '    "watch ./my-project for changes"'
    echo ""
}

# Run all steps
detect_and_install_deps
check_python
install_ocview
setup_bin
setup_config
show_opencode_setup
