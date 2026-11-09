# Wrong: without Restart=, a crash is permanent.
sudo tee /etc/systemd/system/shop-worker.service > /dev/null <<'EOF'
[Unit]
Description=shop-worker: processes the shop's orders

[Service]
ExecStart=/srv/shop-worker/worker.sh
User=shop
WorkingDirectory=/srv/shop-worker

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now shop-worker
