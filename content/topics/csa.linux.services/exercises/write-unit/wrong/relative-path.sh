# Wrong: ExecStart= with no path. systemd looks for a program called
# worker.sh on its own PATH, which has no /srv/shop-worker in it.
sudo tee /etc/systemd/system/shop-worker.service > /dev/null <<'EOF'
[Unit]
Description=shop-worker: processes the shop's orders

[Service]
ExecStart=worker.sh
User=shop
WorkingDirectory=/srv/shop-worker
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now shop-worker || true
