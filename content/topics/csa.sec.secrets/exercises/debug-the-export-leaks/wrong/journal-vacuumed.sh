# Wrong: the journal's old lines are deleted and the logging is left as
# it is, so the next run writes the new key into the journal again.
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
payctl new | cut -d' ' -f2 | sudo tee /etc/shop/paygate.key > /dev/null
payctl revoke k2
sudo journalctl --rotate > /dev/null 2>&1
sudo journalctl --vacuum-time=1s > /dev/null 2>&1
