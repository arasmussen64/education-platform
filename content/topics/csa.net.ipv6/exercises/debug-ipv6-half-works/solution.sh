# The reference fix: each fault fixed at its cause, in r1's files.
# "on MACHINE COMMAND" runs a command on a machine. tee FILE <<'EOF' writes
# the lines up to EOF into FILE; in the lab, nano does the same (sed -i
# can't replace a machine's own file that sits straight in /etc).

# 1. r1 advertised a /56. A host makes its own address only from a /64
#    prefix (its last 64 bits are the host's), so the laptops ignored it.
#    Now r1 advertises the office's subnet.
on r1 tee /etc/radvd.conf > /dev/null << 'EOF'
# r1's router advertisements on the office LAN: the prefix the laptops
# make their own IPv6 addresses from.
interface lan {
    AdvSendAdvert on;
    prefix 2001:db8:42:a::/64 {
        AdvOnLink on;
        AdvAutonomous on;
    };
};
EOF

# 2. r1 forwarded IPv4 only: its sysctl.d file never turned on IPv6
#    forwarding, so it advertised itself as the laptops' router and then
#    dropped everything they sent it. tee -a adds the line to the file.
echo 'net.ipv6.conf.all.forwarding = 1' | on r1 tee -a /etc/sysctl.d/90-forward.conf > /dev/null

# 3. r1's forward chain dropped every ICMPv6 message, "packet too big"
#    included. IPv6 routers never fragment, so a laptop that isn't told a
#    packet was too big keeps sending it, and big uploads hang. The line
#    goes; NDP never crosses a router, so the forward chain doesn't need it.
on r1 tee /etc/nftables.conf > /dev/null << 'EOF'
#!/usr/sbin/nft -f
# r1's firewall and NAT: the office may go out, the internet may not come in.
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iif lo accept
        ct state established,related accept
        meta l4proto ipv6-icmp accept
        iifname "lan" accept
    }
    chain forward {
        type filter hook forward priority filter; policy drop;
        ct state established,related accept
        iifname "lan" oifname "wan" accept
    }
}

table ip nat {
    chain postrouting {
        type nat hook postrouting priority srcnat; policy accept;
        oifname "wan" masquerade
    }
}
EOF

# Build the network again from the files, as a reboot would.
sudo netlab restart

# Look: wait for h1's own address, then ask web which address it sees.
for _ in $(seq 1 15); do
  on h1 ip -6 addr show dev eth0 scope global | grep dynamic > /dev/null && break
  sleep 1
done
on h1 ip -6 addr show dev eth0 scope global
on h1 nc -6 -w 3 2001:db8:80::80 8080 < /dev/null
