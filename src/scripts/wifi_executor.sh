#!/bin/bash
# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Date: 2025-07-27
# Purpose: Runs initial wifi config, sets up project structure

# ==== Configuration ====
USER_NAME="WIFI"
PROJECT_NAME="setup"
DEST_BASE="/home/kipr/Documents/KISS"
USERS_FILE="/home/kipr/Documents/KISS/users.json"
SRC_WIFI_FOLDER_NAME="src_WIFI"

# ==== Skript-Verzeichnis bestimmen ====
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(realpath "$SCRIPT_DIR/..")"
ROOT_DIR="$(realpath "$SCRIPT_DIR/../..")"   # zwei Ebenen hoch = Projekt-Stammverzeichnis

WIFI_INIT_SCRIPT="$SRC_DIR/WIFI_FOR_INSTALLATION/main.py"

# ==== Step 0: Activate WiFi Scan ====
echo "Enabling wifi scan ..."
nmcli dev disconnect wlan0
sleep 2
nmcli dev set wlan0 managed yes
sleep 5
echo "Wifi-scan should be active."

# ==== Step 1: Run WIFI_FOR_INSTALLATION/main.py ====
if [ -f "$WIFI_INIT_SCRIPT" ]; then
    echo "Running initial WiFi script: $WIFI_INIT_SCRIPT"
    python3 "$WIFI_INIT_SCRIPT"
else
    echo "==========ERROR: $WIFI_INIT_SCRIPT not found!=========="
    exit 1
fi

# ==== Step 2: Locate USB project path (relativ) ====
USB_EDITME_PATH=""
if [ -d "$SRC_DIR/EDITME_USER/EDITME_PROJECT" ]; then
    USB_EDITME_PATH="$SRC_DIR/EDITME_USER/EDITME_PROJECT"
fi

if [ -z "$USB_EDITME_PATH" ]; then
    echo "==========EDITME_USER/EDITME_PROJECT not found relative to script!=========="
    exit 1
fi

# ==== Step 3: Replace placeholder in project.manifest ====
MANIFEST_PATH="$USB_EDITME_PATH/project.manifest"
TMP_MANIFEST="/tmp/project.manifest"

if [ -f "$MANIFEST_PATH" ]; then
    sed "s/\"user\":\"EDITME_USER\"/\"user\":\"$USER_NAME\"/" "$MANIFEST_PATH" > "$TMP_MANIFEST"
    echo "Updated project.manifest for user: $USER_NAME"
else
    echo "==========project.manifest not found=========="
    exit 1
fi

# ==== Step 4: Create destination and copy structure ====
DEST="$DEST_BASE/$USER_NAME/$PROJECT_NAME"
mkdir -p "$DEST"
cp -r "$USB_EDITME_PATH"/* "$DEST"
cp "$TMP_MANIFEST" "$DEST/project.manifest"

echo "Copied project to $DEST"

# ==== Step 5: Copy src_WIFI files (relativ) ====
USB_SRC_WIFI="$SRC_DIR/$SRC_WIFI_FOLDER_NAME"

if [ ! -d "$USB_SRC_WIFI" ]; then
    echo "=========='$SRC_WIFI_FOLDER_NAME' not found relative to script!=========="
    exit 1
fi

cp -r "$USB_SRC_WIFI"/* "$DEST/bin/"
cp -r "$USB_SRC_WIFI"/* "$DEST/src/"

chmod -R 777 "$DEST_BASE/"*   # PRISM7k's glory idea -> lets you compile and run the programs

echo "Copied and chmod applied to $DEST"

# ==== Step 6: Replace placeholders inside files ====
find "$DEST_BASE" -type f -exec sed -i "s/EDITME_USER/$USER_NAME/g" {} \;
find "$DEST_BASE" -type f -exec sed -i "s/EDITME_PROJECT/$PROJECT_NAME/g" {} \;

# ==== Step 7: Create symlink for botball_user_program ====
LINK_PATH="$DEST/bin/botball_user_program"
TARGET_PATH="$DEST/bin/main.py"
if [ -f "$TARGET_PATH" ]; then
    ln -sf "$TARGET_PATH" "$LINK_PATH"
    echo "Symlink created: $LINK_PATH → $TARGET_PATH"
else
    echo "main.py not found at $TARGET_PATH!"
fi

# ==== Step 8: Add user to users.json ====
if ! grep -q "\"$USER_NAME\"" "$USERS_FILE"; then
    sed -i '$ s/}$/,"'"$USER_NAME"'":{"mode":"Simpel"}}/' "$USERS_FILE"
    echo "User $USER_NAME added to users.json."
else
    echo "User $USER_NAME already exists in users.json."
fi

# ==== Step 9: Copy LOCAL_STD_WIFI_CONFI.conf to /usr/lib ====
CONF_FILE="$ROOT_DIR/LOCAL_STD_WIFI_CONFI.conf"
DEST_CONF="/usr/lib/LOCAL_STD_WIFI_CONFI.conf"

if [ -f "$CONF_FILE" ]; then
    cp "$CONF_FILE" "$DEST_CONF"
    chmod 644 "$DEST_CONF"
    echo "Copied LOCAL_STD_WIFI_CONFI.conf to $DEST_CONF"
else
    echo "==========ERROR: LOCAL_STD_WIFI_CONFI.conf not found at $CONF_FILE=========="
fi

# ==== Step 10: Sync Time and Firewall Port ====
apt install -y ntp ca-certificates
systemctl enable ntp
systemctl start ntp
update-ca-certificates

# ==== Step 11: Install Python dependencies ====
echo "Installing required Python packages ..."
apt install -y python3-pip
pip3 install scipy --upgrade --target /usr/lib/python3/dist-packages 

# ==== Step 12: Open port for Harrogate ====
sudo iptables -I INPUT -p tcp --dport 8888 -j ACCEPT
sudo sh -c "iptables-save > /etc/iptables/rules.v4"

echo ""
echo "Setup complete."
