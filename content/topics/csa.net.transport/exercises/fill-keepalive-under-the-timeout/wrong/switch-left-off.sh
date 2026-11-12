# Wrong: the system's timers are right and saved, but stock-sync never
# switches keepalive on for its connection, so the timers apply to nothing.
on app tee /etc/sysctl.d/60-keepalive.conf > /dev/null << 'EOF'
net.ipv4.tcp_keepalive_time = 10
net.ipv4.tcp_keepalive_intvl = 5
net.ipv4.tcp_keepalive_probes = 3
EOF
on app sysctl -p /etc/sysctl.d/60-keepalive.conf
on app tee /etc/shop/stock-sync.conf > /dev/null << 'EOF'
supplier = 10.0.2.30:6000
timeout = 4
keepalive = off
EOF
sudo systemctl restart stock-sync@app
