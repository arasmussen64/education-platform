# Wrong: the timers beat nat's 20 s but not the supplier's 12 s: the first
# probe comes after 18 s of quiet, when the supplier's firewall has already
# forgotten the connection. Saved, applied, and keepalive asked for.
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
