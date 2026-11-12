# Wrong: instead of probing sooner, the supplier's firewall is made to
# remember quiet connections for an hour, and the timers only beat nat's.
# The supplier's box isn't the shop's to change.
on supplier sysctl -w net.netfilter.nf_conntrack_tcp_timeout_established=3600
on app tee /etc/sysctl.d/60-keepalive.conf > /dev/null << 'EOF'
net.ipv4.tcp_keepalive_time = 18
net.ipv4.tcp_keepalive_intvl = 5
net.ipv4.tcp_keepalive_probes = 3
EOF
on app sysctl -p /etc/sysctl.d/60-keepalive.conf
on app tee /etc/shop/stock-sync.conf > /dev/null << 'EOF'
supplier = 10.0.2.30:6000
timeout = 4
keepalive = on
EOF
sudo systemctl restart stock-sync@app
