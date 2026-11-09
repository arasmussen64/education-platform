# The three mistakes, in the order they show up:
#   1. The section was called [Services]. systemd ignores a section it doesn't
#      know, so the unit had no ExecStart= and couldn't load ("bad-setting"
#      in systemctl status).
#   2. User=shop-api names an account that doesn't exist; systemd failed at
#      "step USER" (status 217/USER). The account is shop.
#   3. PORT=80800 isn't a port. The program said so in the journal and exited,
#      and systemd kept restarting it.
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
sudo systemctl restart shop-api
sleep 1  # give it a moment to start listening
curl http://localhost:8080/
