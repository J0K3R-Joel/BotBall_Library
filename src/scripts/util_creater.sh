#!/bin/bash
# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Date: 2026-02-12
# Purpose: Create utility files for the python classes

# ==== Configuration ====
DEST_BASE="/home/kipr/BotBall-data"
UTIL_ORIGINAL_FOLDER_NAME="util"

# ==== Skript-Verzeichnis bestimmen ====
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(realpath "$SCRIPT_DIR/..")"

# ==== Find the util folder relative to script ====
USB_UTIL_PATH="$SRC_DIR/$UTIL_ORIGINAL_FOLDER_NAME"

if [ ! -d "$USB_UTIL_PATH" ]; then
    echo "==========util folder not found relative to script!=========="
    exit 1
fi

# ==== Copy all the util files from the USB-Stick to the destination ====
DEST_DIR="$DEST_BASE/util_files"

if [ -d "$DEST_DIR" ]; then
    echo "Destination folder already exists: $DEST_DIR"
    echo "Nothing copied."
    exit 0
fi

mkdir -p "$DEST_DIR"
cp -r "$USB_UTIL_PATH"/* "$DEST_DIR"

sleep 2

chmod -R 777 "$DEST_BASE/util_files"  # Manuel Zöttel's glory idea -> lets you compile and run the programs

echo "Util files copied to $DEST_BASE/util_files."

# ==== Ending message ====
IP_ADDR=$(hostname -I | awk '{print $1}')
echo ""
echo "Util-script finished."
