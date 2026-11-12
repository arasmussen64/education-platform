# Wrong: instead of keepalive datagrams, nat is made to remember UDP
# mappings for an hour. nat stands for the cloud's NAT gateway and isn't the
# shop's to change. Everything else is right.
on nat sysctl -w net.netfilter.nf_conntrack_udp_timeout=3600 net.netfilter.nf_conntrack_udp_timeout_stream=3600
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
sudo systemctl restart shop-api@app feed-client@app
