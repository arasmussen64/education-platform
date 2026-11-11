# Wrong: 3M. To systemd, M is a million bytes (MB), so this allows
# 3,000,000 bytes a second, not the 3 MiB (3,145,728) the tier gives.
sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null <<'EOF'
[Service]
IOWriteIOPSMax=/dev/lab/data 300
IOWriteBandwidthMax=/dev/lab/data 3M
EOF
sudo systemctl daemon-reload
sudo systemctl restart shop-db
