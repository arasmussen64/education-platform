# Wrong: 50-repl.conf is applied by hand, so the keepalive timers are right
# until the next boot, when the vendor's file, read after it, sets the two
# hours again. The other two faults are fixed properly.
sudo sed -i '/^# TCP normalisation/,/^}/d' /etc/netns/edge/nftables.conf
sudo systemctl reload nftables@edge
echo 'net.ipv4.tcp_rmem = 4096 131072 6291456' | on dr tee /etc/sysctl.d/60-tuning.conf > /dev/null
on dr sysctl -p /etc/sysctl.d/60-tuning.conf > /dev/null
on app sysctl -p /etc/sysctl.d/50-repl.conf > /dev/null
sudo systemctl restart repl-agent@app
