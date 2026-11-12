# Wrong: feed-client sends a keepalive datagram every 12 s, and nat forgets
# a UDP mapping after 10, so most updates find no mapping and are lost.
# Everything else is right.
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
standby_connect_timeout = 3
EOF
on app tee /etc/shop/feed.conf > /dev/null << 'EOF'
feed = 10.0.2.40:5005
keepalive_every = 12
EOF
sudo systemctl restart shop-api@app feed-client@app
