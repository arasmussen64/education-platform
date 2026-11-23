# Wrong: the export still logs at debug level, key and all, and a filter
# between it and the journal takes those lines out. The cause is still
# there: the day the filter changes, the key is back in the journal.
sudo mkdir -p /etc/systemd/system/shop-export.service.d
sudo tee /etc/systemd/system/shop-export.service.d/key-file.conf > /dev/null << 'EOF'
[Service]
EnvironmentFile=
ExecStart=
ExecStart=/bin/sh -c "/usr/local/bin/shop-export --api-key-file /etc/shop/paygate.key | grep -v DEBUG"
EOF
sudo systemctl daemon-reload
payctl revoke k1
sudo install -m 400 -o export -g export /dev/null /etc/shop/paygate.key
payctl new | cut -d' ' -f2 | sudo tee /etc/shop/paygate.key > /dev/null
payctl revoke k2
sudo rm /etc/shop/export.env
