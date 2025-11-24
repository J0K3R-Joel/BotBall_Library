#!/bin/bash
# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Date: 2025-09-16
# Purpose: Create the server for the communication

# ==== Configuration ====
USER_NAME="Fake-Server"
PROJECT_NAME="setup"
DEST_BASE="/home/kipr/Documents/KISS"
USERS_FILE="/home/kipr/Documents/KISS/users.json"
SRC_FAKE_SERVER_FOLDER_NAME="src_Fake-Server"

# ==== Declare script folder ====
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(realpath "$SCRIPT_DIR/..")"

# ==== Find the USB-project folder (relativ) ====
USB_EDITME_PATH=""
if [ -d "$SRC_DIR/EDITME_USER/EDITME_PROJECT" ]; then
    USB_EDITME_PATH="$SRC_DIR/EDITME_USER/EDITME_PROJECT"
fi

if [ -z "$USB_EDITME_PATH" ]; then
    echo "==========EDITME_USER/EDITME_PROJECT not found relative to script!=========="
    exit 1
fi

# ==== Replace placeholder in project.manifest (only in copy, not on the USB!) ====
MANIFEST_PATH="$USB_EDITME_PATH/project.manifest"
TMP_MANIFEST="/tmp/project.manifest"

if [ -f "$MANIFEST_PATH" ]; then
    sed "s/\"user\":\"EDITME_USER\"/\"user\":\"$USER_NAME\"/" "$MANIFEST_PATH" > "$TMP_MANIFEST"
    echo "User in replace project.manifest: $USER_NAME"
else
    echo "==========project.manifest not found!=========="
    exit 1
fi

# ==== Create target path ====
DEST="$DEST_BASE/$USER_NAME/$PROJECT_NAME"
mkdir -p "$DEST"

# ==== Copy project structure ====
cp -r "$USB_EDITME_PATH"/* "$DEST"
cp "$TMP_MANIFEST" "$DEST/project.manifest"

echo "Projectpath copied to '$DEST'."

# ==== Paste src_Fake-Server in bin/ and src/ (relativ) ====
USB_SRC_FAKE_SERVER="$SRC_DIR/$SRC_FAKE_SERVER_FOLDER_NAME"

if [ ! -d "$USB_SRC_FAKE_SERVER" ]; then
    echo "=========='$SRC_FAKE_SERVER_FOLDER_NAME' folder not found relative to script!=========="
    exit 1
fi

cp -r "$USB_SRC_FAKE_SERVER"/* "$DEST/bin/"
cp -r "$USB_SRC_FAKE_SERVER"/* "$DEST/src/"

rm -rf $DEST/bin/DELME
rm -rf $DEST/data/DELME
rm -rf $DEST/include/DELME
rm -rf $DEST/src/DELME

chmod -R 777 "$DEST_BASE/"*  # Manuel Zöttel's glory idea -> lets you compile and run the programs

echo "src_Fake-Server files copied to bin/ and src/."

# ==== Replace EDITME_USER and EDITME_PROJECT in the target ====
find "$DEST_BASE" -type f -exec sed -i "s/EDITME_USER/$USER_NAME/g" {} \;
find "$DEST_BASE" -type f -exec sed -i "s/EDITME_PROJECT/$PROJECT_NAME/g" {} \;

echo "Placeholder EDITME_USER/EDITME_PROJECT replaced."

# ==== Create botball_user_program link ====
LINK_PATH="$DEST/bin/botball_user_program"
TARGET_PATH="$DEST/bin/main.py"

if [ -f "$TARGET_PATH" ]; then
    ln -sf "$TARGET_PATH" "$LINK_PATH"
    echo "Link created: $LINK_PATH → $TARGET_PATH"
else
    echo "==========Hint: '$TARGET_PATH' not found. No Link created=========="
fi

# ==== Add User to users.json ====
if ! grep -q "\"$USER_NAME\"" "$USERS_FILE"; then
    sed -i '$ s/}$/,"'"$USER_NAME"'":{"mode":"Simpel"}}/' "$USERS_FILE"
    echo "User $USER_NAME added to users.json."
else
    echo "==========User $USER_NAME exists already in users.json.=========="
fi

# ==== Execute main.py if present ====
MAIN_PY="$DEST/bin/main.py"
if [ -f "$MAIN_PY" ]; then
    echo "Starting main.py ..."
    python3 "$MAIN_PY"
else
    echo "==========main.py not found at '$MAIN_PY'.=========="
    exit 1
fi

# ==== Ending message ====
echo ""
echo "Fake_Server-script finished."