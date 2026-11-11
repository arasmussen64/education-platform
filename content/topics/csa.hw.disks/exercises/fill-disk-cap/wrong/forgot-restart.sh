# Wrong: the drop-in is right, but systemd was never told to read it
# again and the service never restarted, so nothing holds the database.
sudo tee /etc/systemd/system/shop-db.service.d/tier.conf > /dev/null <<'EOF'
[Service]
IOWriteIOPSMax=/dev/lab/data 300
IOWriteBandwidthMax=/dev/lab/data 3145728
EOF
