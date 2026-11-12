# Wrong: the database's firewall is emptied, so nothing there forgets the
# connection, and the keepalive only beats nat's 18 s. The firewall stands
# for the cloud's and isn't the shop's to change. Everything else is right.
on db nft flush ruleset
on app tee /etc/shop/api.conf > /dev/null << 'EOF'
db_host = 10.0.2.20
db_port = 5432
db_query_timeout = 5
db_pool = on
db_keepalive = on
db_keepalive_idle = 15
db_keepalive_interval = 4
db_keepalive_count = 5
standby_host = 10.0.2.21
standby_port = 5432
standby_connect_timeout = 3
EOF
on app tee /etc/shop/feed.conf > /dev/null << 'EOF'
feed = 10.0.2.40:5005
keepalive_every = 5
EOF
sudo systemctl restart shop-api@app feed-client@app
