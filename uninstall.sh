#!/bin/bash
set -e

INSTALL_DIR="$HOME/.local/share/ocview"
BIN_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/ocview"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_ok()   { echo -e "${GREEN}[✓]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[!]${NC} $1"; }

echo ""
echo "  ocview uninstaller"
echo ""

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    print_ok "Removed $INSTALL_DIR"
else
    print_warn "Installation directory not found: $INSTALL_DIR"
fi

# Remove bin symlink
if [ -L "$BIN_DIR/ocview" ] || [ -f "$BIN_DIR/ocview" ]; then
    rm -f "$BIN_DIR/ocview"
    print_ok "Removed $BIN_DIR/ocview"
else
    print_warn "ocview symlink not found in $BIN_DIR"
fi

# Ask about config
if [ -d "$CONFIG_DIR" ]; then
    read -p "Remove config directory $CONFIG_DIR? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$CONFIG_DIR"
        print_ok "Removed $CONFIG_DIR"
    else
        print_warn "Config kept at $CONFIG_DIR"
    fi
fi

echo ""
echo -e "${GREEN}ocview uninstalled.${NC}"
echo ""
