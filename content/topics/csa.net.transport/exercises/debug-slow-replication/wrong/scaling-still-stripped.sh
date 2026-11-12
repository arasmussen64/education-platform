# Wrong: two of the three faults are fixed; edge still removes window
# scaling from every new connection.
echo 'net.ipv4.tcp_rmem = 4096 131072 6291456' | on dr tee /etc/sysctl.d/60-tuning.conf > /dev/null
on dr sysctl -p /etc/sysctl.d/60-tuning.conf > /dev/null
sudo sed -i '/tcp_keepalive_time/d' /etc/netns/app/sysctl.d/99-vendor-tuning.conf
on app sysctl -p /etc/sysctl.d/50-repl.conf > /dev/null
sudo systemctl restart repl-agent@app
