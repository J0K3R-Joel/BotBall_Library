#!/bin/bash
# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com

# Absolute path to this file
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$BASE_DIR/src/scripts"

echo "Starting selected scripts in defined order from: $SCRIPTS_DIR"
echo "------------------------------------------------------------"

# Define prioritized scripts (in order)
PRIORITY_SCRIPTS=("replace_fs.sh" "wifi_executor.sh" "setup_harrogate.sh" "comm_executor.sh" "bias_creater.sh" "base_executor.sh" "camera_executor.sh" "fake_client_executor.sh" "fake_server_executor.sh" "bias_executor.sh")

# Define the script that must be executed last
FINAL_SCRIPT="wifi_finisher.sh"
FINAL_SCRIPT_PATH="$SCRIPTS_DIR/$FINAL_SCRIPT"

# Step 1: Run prioritized scripts
for script_name in "${PRIORITY_SCRIPTS[@]}"; do
    script_path="$SCRIPTS_DIR/$script_name"
    if [ -f "$script_path" ]; then
        echo "Executing (priority): $script_path"
        chmod +x "$script_path"
        "$script_path"
        echo "Finished: $script_path"
        echo "---------------------------"
    else
        echo "==========Warning: $script_path not found!=========="
    fi
done

# Step 2: Run other scripts (excluding priority + final)
for script in "$SCRIPTS_DIR"/*.sh; do
    script_filename="$(basename "$script")"

    if [[ " ${PRIORITY_SCRIPTS[*]} " =~ " $script_filename " ]] || [[ "$script_filename" == "$FINAL_SCRIPT" ]]; then
        continue
    fi

    if [ -f "$script" ]; then
        echo "Executing (other): $script"
        chmod +x "$script"
        "$script"
        echo "Finished: $script"
        echo "---------------------------"
    fi
done

# Step 3: Run the final script
if [ -f "$FINAL_SCRIPT_PATH" ]; then
    echo "Executing (final): $FINAL_SCRIPT_PATH"
    chmod +x "$FINAL_SCRIPT_PATH"
    "$FINAL_SCRIPT_PATH"
    echo "Finished: $FINAL_SCRIPT_PATH"
    echo "---------------------------"
else
    echo "==========Warning: $FINAL_SCRIPT_PATH not found!=========="
fi

echo "All scripts executed successfully."

# Step 4: Set the ownership of specific paths
chmod -R 777 "/usr/lib/bias_files"
chmod 777 /usr/lib/LOCAL_STD_WIFI.conf
