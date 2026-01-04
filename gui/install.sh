#!/bin/bash
# Installation script for iDevice Manager GUI

set -e

echo "Installing iDevice Manager GUI..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Install PyQt6
echo "Installing PyQt6..."
pip3 install --user PyQt6

# Make the script executable
chmod +x idevice_manager.py

# Optional: Install desktop launcher
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    read -p "Install desktop launcher? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p ~/.local/share/applications
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        sed "s|Exec=.*|Exec=python3 $SCRIPT_DIR/idevice_manager.py|g" idevice-manager.desktop > ~/.local/share/applications/idevice-manager.desktop
        echo "Desktop launcher installed to ~/.local/share/applications/"
    fi
fi

echo ""
echo "✓ Installation complete!"
echo ""
echo "To run the GUI:"
echo "  python3 idevice_manager.py"
echo ""
echo "Or use the application launcher if installed."
