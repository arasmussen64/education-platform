# Wrong: the user and the port are fixed, but the section is still [Services],
# so systemd still sees no ExecStart=.
sudo tee /etc/systemd/system/shop-api.service > /dev/null <<'EOF'
[Unit]
Description=shop-api: the shop's web API
After=network-online.target
Wants=network-online.target

[Services]
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
sudo systemctl restart shop-api || true
