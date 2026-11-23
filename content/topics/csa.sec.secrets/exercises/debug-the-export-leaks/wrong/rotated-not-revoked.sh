# Wrong: the leaks are closed and the job gets a new key, and the key it
# used until now, which has been on a command line and in the journal,
# is left active.
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
payctl new | cut -d' ' -f2 | sudo tee /etc/shop/paygate.key > /dev/null
