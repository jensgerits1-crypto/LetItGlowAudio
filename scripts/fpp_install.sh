#!/bin/bash
set -eu
DIR="$(cd "$(dirname "$0")/.." && pwd)"
# No changes to FPP audio, networking, or show configuration.
mkdir -p /home/fpp/media/logs
cat > /tmp/letitglow-audio.service <<EOF
[Unit]
Description=Let It Glow LAN Audio Test
After=network.target
[Service]
Type=simple
User=fpp
WorkingDirectory=$DIR
ExecStart=/usr/bin/python3 $DIR/server.py
Restart=on-failure
RestartSec=3
[Install]
WantedBy=multi-user.target
EOF
sudo install -m 644 /tmp/letitglow-audio.service /etc/systemd/system/letitglow-audio.service
sudo systemctl daemon-reload
sudo systemctl enable --now letitglow-audio.service
printf '\nOpen http://<FPP-IP>:8098 from a phone on the same Wi-Fi\n'
