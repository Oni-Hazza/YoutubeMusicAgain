#!/bin/bash

# Detect distro
DISTRO_ID=$(grep '^ID=' /etc/os-release | cut -d= -f2 | tr -d '"')
DISTRO_NAME=$(grep '^NAME=' /etc/os-release | cut -d= -f2 | tr -d '"')

echo "Detected distro: $DISTRO_NAME ($DISTRO_ID)"

# Set VLC plugin path based on distro
case "$DISTRO_ID" in
    ubuntu|linuxmint)
        VLC_PLUGIN_PATH="/usr/lib/x86_64-linux-gnu/vlc/plugins"
        ;;
    debian)
        VLC_PLUGIN_PATH="/usr/lib/vlc/plugins"
        ;;
    arch)
        VLC_PLUGIN_PATH="/usr/lib/vlc/plugins"
        ;;
    fedora)
        VLC_PLUGIN_PATH="/usr/lib64/vlc/plugins"
        ;;
    *)
        echo "Unknown distro. Prompting user for VLC plugin path..."
        read -p "Enter VLC plugin path (or press enter to skip): " VLC_PLUGIN_PATH
        ;;
esac

# Write install.sh
cat > install.sh <<EOF
#!/bin/bash

APP_NAME="YT Music"
EXECUTABLE_NAME="ytmusic"
INSTALL_DIR="/opt/ytmusic"
ICON_PATH="icons/icon.png"
DESKTOP_FILE="\$HOME/.local/share/applications/ytmusic.desktop"
EXECUTABLE_SOURCE_PATH="dist/main/ytmusic"
INTERNAL_SOURCE_DIR="dist/main/_internal"
ICON_SOURCE_PATH="\$ICON_PATH"
WRAPPER_SCRIPT_PATH="\$INSTALL_DIR/run.sh"

echo "Installing \$APP_NAME..."

sudo mkdir -p "\$INSTALL_DIR"
sudo cp "\$EXECUTABLE_SOURCE_PATH" "\$INSTALL_DIR/\$EXECUTABLE_NAME"
sudo chmod +x "\$INSTALL_DIR/\$EXECUTABLE_NAME"

if [ -d "\$INTERNAL_SOURCE_DIR" ]; then
    sudo cp -r "\$INTERNAL_SOURCE_DIR" "\$INSTALL_DIR/"
    echo "Copied _internal folder to \$INSTALL_DIR/"
fi

sudo mkdir -p "\$INSTALL_DIR/icons"
sudo cp "\$ICON_SOURCE_PATH" "\$INSTALL_DIR/icons/icon.png"

echo "Creating wrapper script..."
sudo tee "\$WRAPPER_SCRIPT_PATH" > /dev/null <<EOW
#!/bin/bash
export VLC_PLUGIN_PATH="$VLC_PLUGIN_PATH"
cd "\$INSTALL_DIR"
./\$EXECUTABLE_NAME > /tmp/ytmusic.log 2>&1
EOW
sudo chmod +x "\$WRAPPER_SCRIPT_PATH"

mkdir -p "\$(dirname "\$DESKTOP_FILE")"
cat > "\$DESKTOP_FILE" <<EOD
[Desktop Entry]
Name=\$APP_NAME
Comment=A desktop YouTube music player
Exec=\$WRAPPER_SCRIPT_PATH
Icon=\$INSTALL_DIR/icons/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Music;Player;
EOD

chmod +x "\$DESKTOP_FILE"
update-desktop-database ~/.local/share/applications/

echo "Installation complete. You can now launch '\$APP_NAME' from the application menu."
EOF

# Write uninstall.sh
cat > uninstall.sh <<EOF
#!/bin/bash

APP_NAME="YT Music"
INSTALL_DIR="/opt/ytmusic"
DESKTOP_FILE="\$HOME/.local/share/applications/ytmusic.desktop"

echo "You are about to uninstall \$APP_NAME."
read -p "Are you sure you want to continue? [y/N]: " confirm

if [[ "\$confirm" =~ ^[Yy]$ ]]; then
    echo "Uninstalling \$APP_NAME..."

    if [ -d "\$INSTALL_DIR" ]; then
        echo "Removing \$INSTALL_DIR..."
        sudo rm -rf "\$INSTALL_DIR"
    else
        echo "No install directory found at \$INSTALL_DIR"
    fi

    if [ -f "\$DESKTOP_FILE" ]; then
        echo "Removing launcher \$DESKTOP_FILE..."
        rm "\$DESKTOP_FILE"
    else
        echo "No .desktop file found at \$DESKTOP_FILE"
    fi

    update-desktop-database ~/.local/share/applications/
    echo "\$APP_NAME has been uninstalled."
else
    echo "Uninstallation cancelled."
fi
EOF

chmod +x install.sh uninstall.sh

echo -e "\n✅ install.sh and uninstall.sh have been generated for $DISTRO_NAME."

