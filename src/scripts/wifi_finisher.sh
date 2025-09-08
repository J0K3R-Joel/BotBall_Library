#!/bin/bash
# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Date: 2025-07-27
# Purpose: Run the actual user project (main.py) that was set up

USER_NAME="WIFI"
PROJECT_NAME="setup"
DEST_BASE="/home/kipr/Documents/KISS"
MAIN_PY="$DEST_BASE/$USER_NAME/$PROJECT_NAME/bin/main.py"

if [ -f "$MAIN_PY" ]; then
    echo "Running main.py ..."
    python3 "$MAIN_PY"
else
    echo "==========ERROR: '$MAIN_PY' not found!=========="
    exit 1
fi

chmod -R 777 "$DEST_BASE/"*   # PRISM7k's glory idea -> lets you compile and run the programs (I had this as my only problem)
