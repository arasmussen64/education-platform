# Wrong: dr's receive buffers are raised live with sysctl -w, and its file
# still caps them, so the next boot brings the cap back. The other two
# faults are fixed properly.
sudo sed -i '/^# TCP normalisation/,/^}/d' /etc/netns/edge/nftables.conf
sudo systemctl reload nftables@edge
on dr sysctl -w net.ipv4.tcp_rmem='4096 131072 6291456'
sudo sed -i '/tcp_keepalive_time/d' /etc/netns/app/sysctl.d/99-vendor-tuning.conf
on app sysctl -p /etc/sysctl.d/50-repl.conf > /dev/null
sudo systemctl restart repl-agent@app
