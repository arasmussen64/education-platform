# Wrong: IOReadIOPSMax caps reads. The database hardly reads, so its
# writes go on at whatever the bytes cap allows, well over 300 a second.
sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null <<'EOF'
[Service]
IOReadIOPSMax=/dev/lab/data 300
IOWriteBandwidthMax=/dev/lab/data 3145728
EOF
sudo systemctl daemon-reload
sudo systemctl restart shop-db
