#!/bin/bash
set -eu
sudo systemctl disable --now letitglow-audio.service || true
sudo rm -f /etc/systemd/system/letitglow-audio.service
sudo systemctl daemon-reload
