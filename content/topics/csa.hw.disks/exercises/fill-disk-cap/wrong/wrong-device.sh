# Wrong: the caps are on the logs disk. The database's tables are on the
# data disk, so its writes aren't held back at all.
sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null <<'EOF'
[Service]
IOWriteIOPSMax=/dev/lab/logs 300
IOWriteBandwidthMax=/dev/lab/logs 3145728
EOF
sudo systemctl daemon-reload
sudo systemctl restart shop-db
