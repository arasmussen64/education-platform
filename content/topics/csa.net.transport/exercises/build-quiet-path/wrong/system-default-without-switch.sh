# Wrong: the system's keepalive timers are set short in app's
# /etc/sysctl.d, but shop-api never switches keepalive on for its
# connection, so the timers apply to nothing. Everything else is right.
on app tee /etc/sysctl.d/60-keepalive.conf > /dev/null << 'EOF'
net.ipv4.tcp_keepalive_time = 8
net.ipv4.tcp_keepalive_intvl = 4
net.ipv4.tcp_keepalive_probes = 5
EOF
on app sysctl -p /etc/sysctl.d/60-keepalive.conf > /dev/null
on app tee /etc/shop/api.conf > /dev/null << 'EOF'
db_host = 10.0.2.20
db_port = 5432
db_query_timeout = 5
db_pool = on
db_keepalive = off
standby_host = 10.0.2.21
standby_port = 5432
standby_connect_timeout = 3
EOF
on app tee /etc/shop/feed.conf > /dev/null << 'EOF'
feed = 10.0.2.40:5005
keepalive_every = 5
EOF
sudo systemctl restart shop-api@app feed-client@app
