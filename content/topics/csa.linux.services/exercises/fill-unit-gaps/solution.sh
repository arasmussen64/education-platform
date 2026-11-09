# The finished unit. In the lab you'd fill the four gaps with nano; here the
# whole file is written in one go.
sudo tee /etc/systemd/system/shop-api.service > /dev/null <<'EOF'
[Unit]
Description=shop-api: the shop's web API
After=network-online.target
Wants=network-online.target

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
sleep 1  # give it a moment to start listening
curl http://localhost:8080/
