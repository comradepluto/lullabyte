#!/bin/bash

echo "=== LULLABYTE AUTO-INSTALLER ==="
echo "Detecting Operating System..."

# detect os
if [ -f /etc/redhat-release ] || [ -f /etc/fedora-release ]; then
    echo "Detected: Fedora/RHEL/CentOS/Scientific Linux"
    PKG_MANAGER="dnf"
elif [ -f /etc/debian_version ]; then
    echo "Detected: Debian/Ubuntu/Mint/Kali"
    PKG_MANAGER="apt-get"
elif [ -f /etc/os-release ] && grep -q "like \"Arch\"" /etc/os-release; then
    echo "Detected: Arch Linux/Manjaro"
    PKG_MANAGER="pacman"
elif [ -f /usr/libexec/wlanctl-ng ]; then # simple check for macos (often present) or check path
    if [ -d "/System/Library/Frameworks" ]; then
        echo "Detected: macOS"
        PKG_MANAGER="brew"
    fi
fi

# fallback detection if specific files not found but common paths exist
if [ -z "$PKG_MANAGER" ]; then
    if command -v pacman &> /dev/null; then
        PKG_MANAGER="pacman"
    elif command -v dnf &> /dev/null; then
        PKG_MANAGER="dnf"
    elif command -v apt-get &> /dev/null; then
        PKG_MANAGER="apt-get"
    elif command -v brew &> /dev/null; then
        PKG_MANAGER="brew"
    else
        echo "No native package manager detected. Falling back to pip."
        PKG_MANAGER="pip3"
    fi
fi

echo "Using Package Manager: $PKG_MANAGER"

# define packages needed
PACKAGES=""

if [ "$PKG_MANAGER" = "pacman" ]; then
    PACKAGES="python python-pip python-pillow python-pyqt5"
elif [ "$PKG_MANAGER" = "dnf" ] || [ "$PKG_MANAGER" = "yum" ]; then
    PACKAGES="python3 python3-pip python3-Pillow python3-PyQt5"
elif [ "$PKG_MANAGER" = "apt-get" ]; then
    PACKAGES="python3 python3-pip python3-pil python3-pyqt5"
elif [ "$PKG_MANAGER" = "brew" ]; then
    PACKAGES="py310-pillow py310-pyqt5 requests" # assuming python 3.10, adjust if needed
fi

# install via package manager
if [ -n "$PACKAGES" ] && [ "$PKG_MANAGER" != "pip3" ]; then
    echo "Installing system dependencies..."
    
    if [ "$PKG_MANAGER" = "pacman" ]; then
        sudo $PKG_MANAGER -S --noconfirm $PACKAGES 2>/dev/null || {
            echo "Native install failed or partial. Falling back to pip."
            PKG_MANAGER="pip3"
        }
    else
        sudo $PKG_MANAGER update && sudo $PKG_MANAGER install -y $PACKAGES 2>/dev/null || {
            echo "Native install failed or partial. Falling back to pip."
            PKG_MANAGER="pip3"
        }
    fi
fi

# final fallback: install via pip if not already done or as last resort
if [ "$PKG_MANAGER" = "pip3" ]; then
    echo "Installing dependencies via pip..."
    python3 -m pip install --upgrade pip
    python3 -m pip install PyQt5 Pillow requests
fi

echo ""
echo "=== INSTALLATION COMPLETE ==="
echo "Running Lullabyte..."
python3 lullabyte.py
