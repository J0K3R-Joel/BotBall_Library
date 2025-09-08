#!/bin/bash
# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Date: 2025-07-28
# Purpose: One-time setup script for Harrogate launcher autostart via systemd

set -e

LAUNCHER_PATH="/home/kipr/harrogate-launch.sh"
SERVICE_PATH="/etc/systemd/system/wombat-launcher.service"
LOGFILE="/var/log/wombat_launcher.log"

echo "[1/5] Creating launcher script at $LAUNCHER_PATH"
sudo tee "$LAUNCHER_PATH" > /dev/null <<'EOF'
#!/bin/bash
# Launch script for Harrogate Web IDE

LOGFILE="/var/log/wombat_launcher.log"

# Create and configure log file
sudo touch "$LOGFILE"
sudo chmod 666 "$LOGFILE"
> "$LOGFILE"

sudo chmod -R 777 /home/kipr/Documents/KISS

# Redirect output to log
exec >> "$LOGFILE" 2>&1

echo "[DEBUG] Script started at $(date)"

# Set library path
export LD_LIBRARY_PATH=/usr/local/qt6/lib:/usr/local/lib

# Start Harrogate server
cd /home/kipr/harrogate || exit 1
echo "[WOMBAT] Starting Harrogate server..."

# Replace the bash process with the node process (systemd will monitor it)
exec /usr/bin/node server.js
EOF

echo "Launcher script created."

echo "[2/5] Making launcher script executable"
sudo chmod +x "$LAUNCHER_PATH"

echo "[3/5] Creating systemd service at $SERVICE_PATH"
sudo tee "$SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Wombat Launcher Autostart
After=network.target

[Service]
Type=simple
User=kipr
WorkingDirectory=/home/kipr
ExecStart=/bin/bash $LAUNCHER_PATH
Restart=on-failure
Environment=NODE_ENV=production
Environment=PORT=8888

[Install]
WantedBy=multi-user.target
EOF

echo "[4/5] Enabling and starting service"
sudo systemctl daemon-reload
sudo systemctl enable wombat-launcher.service
sudo systemctl restart wombat-launcher.service

echo "[5/5] Checking service status:"
sudo systemctl status wombat-launcher.service --no-pager

echo ""
echo "Setup complete! Harrogate server will now auto-launch at boot."
echo "Log output: $LOGFILE"
