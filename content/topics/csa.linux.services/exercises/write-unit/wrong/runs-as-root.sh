# Wrong: no User= line, so the worker runs as root.
sudo tee /etc/systemd/system/shop-worker.service > /dev/null <<'EOF'
[Unit]
Description=shop-worker: processes the shop's orders

[Service]
ExecStart=/srv/shop-worker/worker.sh
WorkingDirectory=/srv/shop-worker
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now shop-worker
