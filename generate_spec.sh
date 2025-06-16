#!/bin/bash

set -e

echo "🔍 Detecting OS..."
OS="$(uname -s)"
IS_WINDOWS=0

if [[ "$OS" == "Linux" ]]; then
    if grep -qi microsoft /proc/version 2>/dev/null; then
        IS_WINDOWS=1  # WSL
    else
        IS_WINDOWS=0
    fi
else
    IS_WINDOWS=1
fi

echo "📁 Preparing output directories..."
mkdir -p pyinstaller_bundle/vlc/plugins
mkdir -p pyinstaller_bundle/libs

if [[ "$IS_WINDOWS" -eq 0 ]]; then
    # Read Linux distro
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        DISTRO=$ID
    else
        DISTRO="unknown"
    fi

    echo "🔍 Detected Linux distro: $DISTRO"

    case "$DISTRO" in
        ubuntu | linuxmint)
            LIBVLC_SRC="/usr/lib/x86_64-linux-gnu/libvlc.so.5"
            LIBVLCCORE_SRC="/usr/lib/x86_64-linux-gnu/libvlccore.so.9"
            VLC_PLUGINS_SRC="/usr/lib/x86_64-linux-gnu/vlc/plugins"
            ;;
        debian)
            LIBVLC_SRC="/usr/lib/libvlc.so.5"
            LIBVLCCORE_SRC="/usr/lib/libvlccore.so.9"
            VLC_PLUGINS_SRC="/usr/lib/vlc/plugins"
            ;;
        fedora)
            LIBVLC_SRC="/usr/lib64/libvlc.so.5"
            LIBVLCCORE_SRC="/usr/lib64/libvlccore.so.9"
            VLC_PLUGINS_SRC="/usr/lib64/vlc/plugins"
            ;;
        *)
            echo "⚠️  Unknown Linux distro: $DISTRO"
            echo "🔧 Please enter the full paths manually:"

            read -rp "Path to libvlc.so.5: " LIBVLC_SRC
            read -rp "Path to libvlccore.so.9: " LIBVLCCORE_SRC
            read -rp "Path to VLC plugins directory: " VLC_PLUGINS_SRC

            if [[ ! -f "$LIBVLC_SRC" || ! -f "$LIBVLCCORE_SRC" || ! -d "$VLC_PLUGINS_SRC" ]]; then
                echo "❌ One or more paths are invalid. Please check and try again."
                exit 1
            fi
            ;;
    esac

    echo "📁 Copying VLC libraries and plugins..."
    cp "$LIBVLC_SRC" pyinstaller_bundle/libs/
    cp "$LIBVLCCORE_SRC" pyinstaller_bundle/libs/
    cp -r "$VLC_PLUGINS_SRC/"* pyinstaller_bundle/vlc/plugins/

    LIBVLC_PATH="pyinstaller_bundle/libs/$(basename "$LIBVLC_SRC")"
    LIBVLCCORE_PATH="pyinstaller_bundle/libs/$(basename "$LIBVLCCORE_SRC")"
    VLC_PLUGINS="pyinstaller_bundle/vlc/plugins"

else
    echo "🔵 Windows detected (or WSL). Please manually copy VLC DLLs and plugins."

    LIBVLC_PATH="pyinstaller_bundle/libs/libvlc.dll"
    LIBVLCCORE_PATH="pyinstaller_bundle/libs/libvlccore.dll"
    VLC_PLUGINS="pyinstaller_bundle/vlc/plugins"
fi

echo "📝 Generating main.spec..."

cat > main.spec <<EOF
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

block_cipher = None

project_root = os.path.abspath(".")

submodules = ['widgets', 'youtubefunc']
data_modules = ['widgets', 'icons', 'youtubefunc']

all_hiddenimports = sum([collect_submodules(m) for m in submodules], [])
all_datas = sum([collect_data_files(m) for m in data_modules], [])

binaries = [
    ('$LIBVLC_PATH', '.'),
    ('$LIBVLCCORE_PATH', '.'),
]

all_datas += [
    ('$VLC_PLUGINS', 'vlc/plugins'),
]

a = Analysis(
    ['main.py', 'resources.py'],
    pathex=[project_root],
    binaries=binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ytmusic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon='icons/icon.png'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
EOF

echo "✅ Done! main.spec and dependencies are ready."
