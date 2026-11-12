# A reference solution, with the evidence that leads to each fault. Files
# are written whole with "on MACHINE tee FILE << 'EOF'": tee, as root on
# that machine, writes what follows, up to the line EOF, into the file
# (nano does the same by hand).
#
# The replication is slow: about 5 Mbit/s of 50. One connection carries at
# most one window per round trip, so look at the window: the SYN leaving
# app offers wscale 10, and the same SYN arriving at dr offers nothing in
# its place but nops. Something between them removes it: edge's firewall.
on app iperf3 -c 10.0.6.20 -t 5
on app timeout 4 tcpdump -nn -i eth0 'tcp[tcpflags] & tcp-syn != 0 and port 5201' &
on dr timeout 4 tcpdump -nn -i eth0 'tcp[tcpflags] & tcp-syn != 0 and port 5201' &
sleep 1; on app iperf3 -c 10.0.6.20 -t 1 > /dev/null; wait
on edge nft list ruleset
# Fault 1: edge's "normalise" table resets the window scale option in every
# SYN. The table goes from edge's file, and the file is loaded again.
on edge tee /etc/nftables.conf << 'EOF'
#!/usr/sbin/nft -f
# edge: the site's firewall towards the private link. app may start
# connections out, with its address translated to edge's own; nothing
# outside may start one in. Connections are tracked, and one that has been
# quiet for longer than edge's idle timer is forgotten.
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iif lo accept
        ct state established,related accept
        iifname "inside" accept
    }
    chain forward {
        type filter hook forward priority filter; policy drop;
        ct state established,related accept
        iifname "inside" oifname "outside" tcp flags & (syn | ack) == syn ct state new accept
        iifname "inside" oifname "outside" meta l4proto { udp, icmp } ct state new accept
    }
}

# The site's address on the link: app's connections leave as edge's.
table ip nat {
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        oifname "outside" masquerade
    }
}
EOF
sudo systemctl reload nftables@edge
# Still only about 9 Mbit/s. The window now scales, but the receiver decides
# how big it may grow: dr's tcp_rmem caps a connection's receive buffer at
# 174,760 bytes, a fraction of the 625,000 bytes this path holds (50 Mbit/s
# for 0.1 s).
on app iperf3 -c 10.0.6.20 -t 5
on dr sysctl net.ipv4.tcp_rmem
on dr cat /etc/sysctl.d/60-tuning.conf
# Fault 2: a maximum of 6 MB, applied now and at every boot.
on dr tee /etc/sysctl.d/60-tuning.conf << 'EOF'
# TCP receive buffer sizes for this server: the minimum, the default and the
# most the kernel may grow one connection's buffer to, in bytes.
net.ipv4.tcp_rmem = 4096 131072 6291456
EOF
on dr sysctl -p /etc/sysctl.d/60-tuning.conf
on app iperf3 -c 10.0.6.20 -t 5
# The status connection: a check, 13 s of quiet, a check. The second fails,
# and ss shows why: the connection's keepalive timer counts down from two
# hours, though 50-repl.conf asks for 5 s. A later file sets it back.
on app curl -s localhost:8090/status
sleep 13
on app curl -s localhost:8090/status
journalctl -u repl-agent@app -n 3
on app ss -tno '( dport = :8443 )'
on app sysctl net.ipv4.tcp_keepalive_time
on app grep -r keepalive /etc/sysctl.d
# Fault 3: the vendor's file, read last, puts keepalive back to 7200 s. Its
# keepalive line goes, 50-repl.conf's timers are applied now, and
# repl-agent opens a new connection, whose timer starts from them.
on app tee /etc/sysctl.d/99-vendor-tuning.conf << 'EOF'
# The database vendor's recommended network settings for its servers.
net.core.somaxconn = 4096
net.ipv4.tcp_fin_timeout = 30
EOF
on app sysctl -p /etc/sysctl.d/50-repl.conf
sudo systemctl restart repl-agent@app
on app curl -s localhost:8090/status
sleep 13
on app curl -s localhost:8090/status
