#!/bin/bash

SERVICE_NAME="wifi-autostart.service"
TARGET_PY="/home/kipr/Documents/KISS/WIFI/setup/bin/main.py"

echo "Creating systemd service…"

# write service-file
sudo bash -c "cat > /etc/systemd/system/$SERVICE_NAME" <<EOF
[Unit]
Description=Starte KISS WIFI main.py beim Booten
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $TARGET_PY
WorkingDirectory=/home/kipr/Documents/KISS/WIFI/setup/bin
User=kipr
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "Activate service…"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "FINISHED! The python script will get executed after every reboot."
