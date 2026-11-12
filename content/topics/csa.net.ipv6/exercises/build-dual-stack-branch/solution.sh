# The reference build. "on MACHINE COMMAND" runs a command on a machine;
# tee FILE <<'EOF' writes the lines up to EOF into FILE, which in the lab
# you'd do with nano (sed -i can't replace a machine's own file that sits
# straight in /etc, like /etc/radvd.conf).
#
# 1. r1's addresses on the branch's switch: the machines' IPv4 gateway,
#    and the first address of subnet 25 of the company's /48. The /64 on
#    lan also gives r1 its route back to the branch.
on r1 tee /etc/network/up > /dev/null << 'EOF'
# r1's network settings, run at every boot: the branch's router.
# The line to the ISP, and the default route of each family through it.
ip addr add 198.51.100.10/30 dev wan
ip addr add 2001:db8:ffff:9::2/64 dev wan
ip route add default via 198.51.100.9
ip route add default via 2001:db8:ffff:9::1
# The branch's switch: the machines' IPv4 gateway, and the first address
# of the branch's subnet, 25 of 2001:db8:c0de::/48.
ip addr add 192.168.20.1/24 dev lan
ip addr add 2001:db8:c0de:25::1/64 dev lan
EOF

# 2. Forwarding, both families, in a file of r1's own kernel settings.
on r1 tee /etc/sysctl.d/90-forward.conf > /dev/null << 'EOF'
# r1 forwards the branch's traffic, in both families.
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
EOF

# 3. Router advertisements of the branch's /64, so the machines build
#    their own addresses and take r1 as their default router.
on r1 tee /etc/radvd.conf > /dev/null << 'EOF'
# r1's router advertisements on the branch's switch: the prefix the
# machines make their own IPv6 addresses from.
interface lan {
    AdvSendAdvert on;
    prefix 2001:db8:c0de:25::/64 {
        AdvOnLink on;
        AdvAutonomous on;
    };
};
EOF

# 4. The firewall: one inet table for both families. Into r1, only the
#    branch, replies, and ICMPv6 (neighbour discovery from the ISP's
#    router too, or r1 can't be found on its own line). Through r1, only
#    the branch going out, and replies, which include the ICMPv6 errors
#    about the branch's own connections, "packet too big" among them.
#    IPv4 alone is translated to r1's address.
on r1 tee /etc/nftables.conf > /dev/null << 'EOF'
#!/usr/sbin/nft -f
# r1's firewall and NAT: the branch may go out, the internet may not come in.
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

# 5. Both services start now and at every boot; then the network is built
#    again from every machine's files, as a reboot would.
sudo systemctl enable --now nftables@r1 radvd@r1
sudo netlab restart

# Look: wait for h1's own address, then ask web which address it sees,
# over each family.
for _ in $(seq 1 10); do
  on h1 ip -6 addr show dev eth0 scope global | grep dynamic > /dev/null && break
  sleep 1
done
on h1 ip -6 addr show dev eth0
on h1 nc -6 -w 3 2001:db8:80::80 8080 < /dev/null
on h1 nc -4 -w 3 203.0.113.80 8080 < /dev/null
