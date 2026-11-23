# Wrong: all three faults are fixed, and the job goes on paying with the
# key it had, moved into a private file. That key has been on a command
# line and in the journal for a month.
sudo sed -i 's/^log_level = .*/log_level = info/' /etc/shop/export.conf
sudo mkdir -p /etc/systemd/system/shop-export.service.d
sudo tee /etc/systemd/system/shop-export.service.d/key-file.conf > /dev/null << 'EOF'
[Service]
EnvironmentFile=
ExecStart=
ExecStart=/usr/local/bin/shop-export --api-key-file /etc/shop/paygate.key
EOF
sudo systemctl daemon-reload
payctl revoke k1
sudo install -m 400 -o export -g export /dev/null /etc/shop/paygate.key
sudo grep -o 'pg_live_.*' /etc/shop/export.env | sudo tee /etc/shop/paygate.key > /dev/null
