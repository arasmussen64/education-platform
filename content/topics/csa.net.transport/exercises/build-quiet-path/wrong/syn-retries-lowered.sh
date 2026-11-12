# Wrong: the standby is reported down in seconds by cutting the system's
# SYN retries to 1 for every program on app, instead of giving shop-api a
# connect timeout of its own. Everything else is right.
on app tee /etc/sysctl.d/60-connect.conf > /dev/null << 'EOF'
net.ipv4.tcp_syn_retries = 1
EOF
on app sysctl -p /etc/sysctl.d/60-connect.conf > /dev/null
on app tee /etc/shop/api.conf > /dev/null << 'EOF'
db_host = 10.0.2.20
db_port = 5432
db_query_timeout = 5
db_pool = on
db_keepalive = on
db_keepalive_idle = 8
db_keepalive_interval = 4
db_keepalive_count = 5
standby_host = 10.0.2.21
standby_port = 5432
EOF
on app tee /etc/shop/feed.conf > /dev/null << 'EOF'
feed = 10.0.2.40:5005
keepalive_every = 5
EOF
sudo systemctl restart shop-api@app feed-client@app
