# Wrong: everything but the persistent journal; a reboot would lose the logs.
sudo tee /etc/systemd/system/shop-api.service > /dev/null <<'EOF'
[Unit]
Description=shop-api: the shop's web API

[Service]
User=shop
WorkingDirectory=/srv/shop-api
Environment=PORT=8080
ExecStart=/usr/bin/python3 /srv/shop-api/server.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now shop-api
sleep 1
curl -s http://localhost:8080/crash || true
sleep 5
mkdir -p ~/report
journalctl -u shop-api -p err -o cat --no-pager > ~/report/errors.txt
systemctl show -p NRestarts --value shop-api > ~/report/restarts.txt
