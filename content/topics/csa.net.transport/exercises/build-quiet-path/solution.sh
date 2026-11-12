# A reference solution. First the boxes' timers: nat forgets a quiet TCP
# connection after 18 s and a UDP mapping after 10 s; the database's
# firewall forgets a quiet connection after 11 s.
#
# 1. shop-api's connection: keepalive on, with its own timers below the
#    smaller box's 11 s (a probe after 8 s of quiet, 4 s between unanswered
#    ones), and a dead database noticed 8 + 4 × 5 = 28 s after the last
#    packet, inside the 60.
# 2. The feed: a keepalive datagram every 5 s, under nat's 10.
# 3. The standby: shop-api's own connect timeout, 3 s, so the system's SYN
#    retries (and every other program's) stay as they are.
# 4. Settings in the two files, which both programs read when they start,
#    and both restarted so they run them now.
# Each file is written whole with "on app tee FILE << 'EOF'": tee, as root
# on app, writes what follows, up to the line EOF, into the file (nano does
# the same by hand).
on nat sysctl net.netfilter.nf_conntrack_tcp_timeout_established net.netfilter.nf_conntrack_udp_timeout net.netfilter.nf_conntrack_udp_timeout_stream
on db sysctl net.netfilter.nf_conntrack_tcp_timeout_established
on app tee /etc/shop/api.conf << 'EOF'
# shop-api's settings, read when it starts (sudo systemctl restart shop-api@app).
# Lines are "name = value"; a later line for the same name wins.

# The orders database, through the NAT gateway.
db_host = 10.0.2.20
db_port = 5432
# How long an order waits for the database's answer, in seconds.
db_query_timeout = 5
# on: keep one connection open and send every order over it.
# off: open a new connection for each order, and close it afterwards.
db_pool = on

# TCP keepalive on the database connection: below the database firewall's
# 11 s, and a dead database noticed after 8 + 4 x 5 = 28 s.
db_keepalive = on
db_keepalive_idle = 8
db_keepalive_interval = 4
db_keepalive_count = 5

# The standby database, which GET /health/standby tries to connect to.
standby_host = 10.0.2.21
standby_port = 5432
# How long to wait for the standby to answer a connection, in seconds.
standby_connect_timeout = 3
EOF
on app tee /etc/shop/feed.conf << 'EOF'
# feed-client's settings, read when it starts (sudo systemctl restart feed-client@app).
# Lines are "name = value"; a later line for the same name wins.

# The supplier's price feed. feed-client subscribes once, when it starts, by
# sending the feed one datagram; the feed then pushes an update every 15
# seconds to every address that has sent it anything.
feed = 10.0.2.40:5005
# A keepalive datagram every 5 s, inside nat's 10 s for a UDP mapping.
keepalive_every = 5
EOF
sudo systemctl restart shop-api@app feed-client@app
on app curl -s localhost:8080/order
on app ss -tno '( dport = :5432 )'
sleep 13
on app curl -s localhost:8080/order
on app curl -s localhost:8080/health/standby
journalctl -u feed-client@app -n 3
