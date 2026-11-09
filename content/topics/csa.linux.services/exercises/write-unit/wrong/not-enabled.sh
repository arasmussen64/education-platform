# Wrong: started, never enabled, so the next boot won't start it.
sudo tee /etc/systemd/system/shop-worker.service > /dev/null <<'EOF'
[Unit]
Description=shop-worker: processes the shop's orders

[Service]
ExecStart=/srv/shop-worker/worker.sh
User=shop
WorkingDirectory=/srv/shop-worker
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl start shop-worker
