# Wrong: two of the three faults are fixed; dr still caps a connection's
# receive buffer at 174,760 bytes.
sudo sed -i '/^# TCP normalisation/,/^}/d' /etc/netns/edge/nftables.conf
sudo systemctl reload nftables@edge
sudo sed -i '/tcp_keepalive_time/d' /etc/netns/app/sysctl.d/99-vendor-tuning.conf
on app sysctl -p /etc/sysctl.d/50-repl.conf > /dev/null
sudo systemctl restart repl-agent@app
