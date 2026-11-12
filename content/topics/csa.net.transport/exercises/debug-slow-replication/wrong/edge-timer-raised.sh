# Wrong: the status connection is kept alive by making edge remember quiet
# connections for an hour, instead of fixing app's keepalive. edge's idle
# timer stands for a managed firewall's and isn't the shop's to change.
# The window scaling and dr's buffers are fixed properly.
sudo sed -i '/^# TCP normalisation/,/^}/d' /etc/netns/edge/nftables.conf
sudo systemctl reload nftables@edge
echo 'net.ipv4.tcp_rmem = 4096 131072 6291456' | on dr tee /etc/sysctl.d/60-tuning.conf > /dev/null
on dr sysctl -p /etc/sysctl.d/60-tuning.conf > /dev/null
on edge sysctl -w net.netfilter.nf_conntrack_tcp_timeout_established=3600
sudo systemctl restart repl-agent@app
