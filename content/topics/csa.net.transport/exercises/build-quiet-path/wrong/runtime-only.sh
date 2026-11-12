# Wrong: shop-api switches keepalive on and leaves the timers to the
# system, and the system's timers are set live with sysctl -w only, so the
# next boot brings back two hours. Everything else is right.
on app sysctl -w net.ipv4.tcp_keepalive_time=8 net.ipv4.tcp_keepalive_intvl=4 net.ipv4.tcp_keepalive_probes=5
on app tee /etc/shop/api.conf > /dev/null << 'EOF'
db_host = 10.0.2.20
db_port = 5432
db_query_timeout = 5
db_pool = on
db_keepalive = on
standby_host = 10.0.2.21
standby_port = 5432
standby_connect_timeout = 3
EOF
on app tee /etc/shop/feed.conf > /dev/null << 'EOF'
feed = 10.0.2.40:5005
keepalive_every = 5
EOF
sudo systemctl restart shop-api@app feed-client@app
