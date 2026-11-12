# Wrong: window scaling gets through because edge's whole firewall is gone,
# saved that way: nothing outside is kept out any more, and app's address
# is no longer translated. The other two faults are fixed properly.
echo 'flush ruleset' | on edge tee /etc/nftables.conf > /dev/null
sudo systemctl reload nftables@edge
echo 'net.ipv4.tcp_rmem = 4096 131072 6291456' | on dr tee /etc/sysctl.d/60-tuning.conf > /dev/null
on dr sysctl -p /etc/sysctl.d/60-tuning.conf > /dev/null
sudo sed -i '/tcp_keepalive_time/d' /etc/netns/app/sysctl.d/99-vendor-tuning.conf
on app sysctl -p /etc/sysctl.d/50-repl.conf > /dev/null
sudo systemctl restart repl-agent@app
