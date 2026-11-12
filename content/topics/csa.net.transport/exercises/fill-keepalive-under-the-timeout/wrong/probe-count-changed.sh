# Wrong: the timers are right for both boxes and saved, but the probe count
# was changed to 6, which the prompt says to leave at 3. (A dead supplier
# is still noticed in 10 + 5 x 6 = 40 s, so only the rule shows it.)
on app tee /etc/sysctl.d/60-keepalive.conf > /dev/null << 'EOF'
net.ipv4.tcp_keepalive_time = 10
net.ipv4.tcp_keepalive_intvl = 5
net.ipv4.tcp_keepalive_probes = 6
EOF
on app sysctl -p /etc/sysctl.d/60-keepalive.conf
on app tee /etc/shop/stock-sync.conf > /dev/null << 'EOF'
supplier = 10.0.2.30:6000
timeout = 4
keepalive = on
EOF
sudo systemctl restart stock-sync@app
