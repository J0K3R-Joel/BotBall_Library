#!/bin/bash
# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Date: 2025-07-28
# Purpose: Create the bias files for the python files

# ==== Configuration ====
DEST_BASE="/usr/lib"
BIAS_FOLDER_NAME="bias"

# ==== Skript-Verzeichnis bestimmen ====
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(realpath "$SCRIPT_DIR/..")"

# ==== Find the bias folder relative to script ====
USB_BIAS_PATH="$SRC_DIR/$BIAS_FOLDER_NAME"

if [ ! -d "$USB_BIAS_PATH" ]; then
    echo "==========bias folder not found relative to script!=========="
    exit 1
fi

# ==== Copy all the bias files from the USB-Stick to the destination ====
mkdir -p "$DEST_BASE/bias_files"
cp -r "$USB_BIAS_PATH"/* "$DEST_BASE/bias_files"

chmod -R 777 "$DEST_BASE/bias_files"/*  # Manuel Zöttel's glory idea -> lets you compile and run the programs

echo "Bias files copied to $DEST_BASE/bias_files."

# ==== Ending message ====
IP_ADDR=$(hostname -I | awk '{print $1}')
echo ""
echo "Bias-script finished."
