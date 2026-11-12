# Wrong: the timers are set live with sysctl -w and the starter file is left
# with its gaps, so the next boot brings back the system's two hours.
on app sysctl -w net.ipv4.tcp_keepalive_time=10 net.ipv4.tcp_keepalive_intvl=5 net.ipv4.tcp_keepalive_probes=3
on app tee /etc/shop/stock-sync.conf > /dev/null << 'EOF'
supplier = 10.0.2.30:6000
timeout = 4
keepalive = on
EOF
sudo systemctl restart stock-sync@app
