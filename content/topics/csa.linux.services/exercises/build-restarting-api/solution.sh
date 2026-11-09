# 1. The unit: the API as the shop user, restarted three seconds after a
#    failure, part of a normally booted server.
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

# 2. A persistent journal: with this folder present, journald keeps the logs
#    on disk instead of in memory. systemd-tmpfiles gives the folder the
#    permissions the journal expects (group systemd-journal, so you can read
#    it), and --flush moves what journald has there now.
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo journalctl --flush

# 3. Crash it, wait out RestartSec, and look.
curl http://localhost:8080/crash
sleep 5
systemctl status shop-api --no-pager
mkdir -p ~/report
journalctl -u shop-api -p err -o cat --no-pager > ~/report/errors.txt
systemctl show -p NRestarts --value shop-api > ~/report/restarts.txt
cat ~/report/errors.txt ~/report/restarts.txt
