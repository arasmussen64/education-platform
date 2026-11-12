# Wrong: the table that strips window scaling is deleted from edge's
# running firewall only; its file still has it, so the next boot brings it
# back. The other two faults are fixed properly.
on edge nft delete table inet normalise
echo 'net.ipv4.tcp_rmem = 4096 131072 6291456' | on dr tee /etc/sysctl.d/60-tuning.conf > /dev/null
on dr sysctl -p /etc/sysctl.d/60-tuning.conf > /dev/null
sudo sed -i '/tcp_keepalive_time/d' /etc/netns/app/sysctl.d/99-vendor-tuning.conf
on app sysctl -p /etc/sysctl.d/50-repl.conf > /dev/null
sudo systemctl restart repl-agent@app
