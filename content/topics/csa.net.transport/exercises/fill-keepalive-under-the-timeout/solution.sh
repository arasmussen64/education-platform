# A reference solution. The two boxes' idle timers first: nat forgets after
# 20 s, the supplier's firewall after 12, so probes must come sooner than
# 12 s. On a quiet connection they come every tcp_keepalive_time or every
# tcp_keepalive_intvl, whichever is longer, so both are under 12: 10 and 5.
# A dead supplier is then noticed 10 + 5 × 3 = 25 s after the last packet.
# Each file is written whole with "on app tee FILE << 'EOF'": tee, as root
# on app, writes what follows, up to the line EOF, into the file (nano does
# the same by hand).
on nat sysctl net.netfilter.nf_conntrack_tcp_timeout_established
on supplier sysctl net.netfilter.nf_conntrack_tcp_timeout_established
on app tee /etc/sysctl.d/60-keepalive.conf << 'EOF'
# Keepalive timers for every program on this machine that switches keepalive
# on for a connection without setting timers of its own (stock-sync does).
# Applied at every boot; "sysctl -p /etc/sysctl.d/60-keepalive.conf" applies
# it now.
net.ipv4.tcp_keepalive_time = 10
net.ipv4.tcp_keepalive_intvl = 5
net.ipv4.tcp_keepalive_probes = 3
EOF
on app sysctl -p /etc/sysctl.d/60-keepalive.conf
on app tee /etc/shop/stock-sync.conf << 'EOF'
# stock-sync's settings, read when it starts (sudo systemctl restart stock-sync@app).
# Lines are "name = value"; a later line for the same name wins.

# The supplier's stock API, through the NAT gateway.
supplier = 10.0.2.30:6000
# How long a sync waits for the supplier's answer, in seconds.
timeout = 4

# TCP keepalive on the connection to the supplier: on or off. stock-sync
# only switches it on or off; the timers are the system's,
# net.ipv4.tcp_keepalive_time, _intvl and _probes.
keepalive = on
EOF
sudo systemctl restart stock-sync@app
on app curl -s localhost:8081/sync
on app ss -tno '( dport = :6000 )'
