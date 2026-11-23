# Wrong: both keys are revoked and the job is given none: nothing leaks,
# and nothing is charged.
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
payctl revoke k2
