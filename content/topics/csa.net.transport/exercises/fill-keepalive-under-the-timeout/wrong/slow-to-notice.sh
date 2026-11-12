# Wrong: the first probe comes in time, but the probes are 30 s apart:
# after an answered probe the next waits 30 s, long after the supplier's
# firewall has forgotten, and a dead supplier would take 10 + 30 × 3 = 100 s
# to notice.
on app tee /etc/sysctl.d/60-keepalive.conf > /dev/null << 'EOF'
net.ipv4.tcp_keepalive_time = 10
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 3
EOF
on app sysctl -p /etc/sysctl.d/60-keepalive.conf
on app tee /etc/shop/stock-sync.conf > /dev/null << 'EOF'
supplier = 10.0.2.30:6000
timeout = 4
keepalive = on
EOF
sudo systemctl restart stock-sync@app
