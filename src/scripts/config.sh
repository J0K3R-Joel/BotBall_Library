#!/bin/bash
# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NEW_DATA_DIR="/home/kipr/BotBall-data"

echo "Starting selected scripts in defined order from: $SCRIPTS_DIR"
echo "------------------------------------------------------------"

# Define prioritized scripts (in order) -> some scripts need to be executed before others
PRIORITY_SCRIPTS=("wifi_executor.sh" "comm_executor.sh" "bias_creater.sh" "util_creater.sh" "base_executor.sh" "camera_executor.sh" "fake_client_executor.sh" "fake_server_executor.sh" "bias_executor.sh" "wifi_setupper.sh")

# Define the script that must be executed last
FINAL_SCRIPT="wifi_finisher.sh"
FINAL_SCRIPT_PATH="$SCRIPTS_DIR/$FINAL_SCRIPT"

# Change permissions for every user and project that gets created (for BotBall)
chmod 777 "/home/kipr/Documents/KISS"/*


# Step 0: Create the folder for every data and log file that gets created by my library
mkdir $NEW_DATA_DIR
chmod 777 $NEW_DATA_DIR

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

    if [[ " ${PRIORITY_SCRIPTS[*]} " =~ " $script_filename " ]] || [[ "$script_filename" == "$FINAL_SCRIPT" ]] || [[ "$script_filename" == "config.sh" ]]; then
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
chmod -R 777 "$NEW_DATA_DIR"/bias_files
chmod -R 777 "$NEW_DATA_DIR"/util_files
chmod 777 "$NEW_DATA_DIR"/LOCAL_STD_WIFI.conf
