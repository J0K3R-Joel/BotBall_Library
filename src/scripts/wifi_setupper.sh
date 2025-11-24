#!/bin/bash

SERVICE_NAME="wifi-autostart.service"
TARGET_PY="/home/kipr/Documents/KISS/WIFI/setup/bin/main.py"

echo "Erstelle systemd Service…"

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

echo "Service aktivieren…"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "FERTIG! Das Python-Skript wird jetzt bei jedem Bootvorgang gestartet."
