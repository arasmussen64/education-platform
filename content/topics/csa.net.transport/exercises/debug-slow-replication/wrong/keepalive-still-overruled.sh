# Wrong: two of the three faults are fixed; the vendor's file still sets
# keepalive back to two hours, so the status connection is cut after a
# quiet spell.
sudo sed -i '/^# TCP normalisation/,/^}/d' /etc/netns/edge/nftables.conf
sudo systemctl reload nftables@edge
echo 'net.ipv4.tcp_rmem = 4096 131072 6291456' | on dr tee /etc/sysctl.d/60-tuning.conf > /dev/null
on dr sysctl -p /etc/sysctl.d/60-tuning.conf > /dev/null
sudo systemctl restart repl-agent@app
