#!/bin/bash
# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Date: 2025-07-27
# Description: Replaces fs.js in harrogate project with the version from USB

# Exit immediately if any command fails
set -e

# ==== Resolve absolute path of the source file ====
SOURCE_REL="./src/replace/fs.js"
SOURCE=$(realpath "$SOURCE_REL")

# Destination
DEST_DIR="/home/kipr/harrogate/apps/fs/api-routes"
DEST_FILE="$DEST_DIR/fs.js"

echo "Replacing fs.js in $DEST_DIR"
echo "Using source file: $SOURCE"

# Check source file exists
if [ ! -f "$SOURCE" ]; then
  echo "======Source file '$SOURCE' not found!======"
  exit 1
fi

# Check destination directory exists
if [ ! -d "$DEST_DIR" ]; then
  echo "======Destination directory '$DEST_DIR' does not exist!======"
  exit 1
fi

# Remove old file
if [ -f "$DEST_FILE" ]; then
  echo "Deleting existing $DEST_FILE"
  rm "$DEST_FILE"
fi

# Copy new file
echo "Copying $SOURCE to $DEST_DIR"
cp "$SOURCE" "$DEST_DIR"

echo "fs.js has been replaced successfully."
