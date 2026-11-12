# Wrong: the health page answers "down" in milliseconds because it no
# longer asks the standby at all: standby_host points at app itself, where
# nothing listens on 5432, so every attempt is refused at once. The
# standby's own state is never looked at. Everything else is right.
on app tee /etc/shop/api.conf > /dev/null << 'EOF'
db_host = 10.0.2.20
db_port = 5432
db_query_timeout = 5
db_pool = on
db_keepalive = on
db_keepalive_idle = 8
db_keepalive_interval = 4
db_keepalive_count = 5
standby_host = 127.0.0.1
standby_port = 5432
EOF
on app tee /etc/shop/feed.conf > /dev/null << 'EOF'
feed = 10.0.2.40:5005
keepalive_every = 5
EOF
sudo systemctl restart shop-api@app feed-client@app
