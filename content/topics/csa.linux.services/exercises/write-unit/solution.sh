# The reference unit, written in one go; in the lab you'd use nano.
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
sudo systemctl enable --now shop-worker
systemctl status shop-worker --no-pager
journalctl -u shop-worker -n 5 --no-pager
