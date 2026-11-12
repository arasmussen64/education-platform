# Wrong: r1 advertises the branch's subnet but has no address in it, so it
# has no route to it either: replies to the branch's machines follow r1's
# default route back to the ISP, which sends them to r1 again.
on r1 tee -a /etc/network/up > /dev/null << 'EOF'
ip addr add 192.168.20.1/24 dev lan
EOF
printf 'net.ipv4.ip_forward = 1\nnet.ipv6.conf.all.forwarding = 1\n' | on r1 tee /etc/sysctl.d/90-forward.conf > /dev/null
printf 'interface lan {\n    AdvSendAdvert on;\n    prefix 2001:db8:c0de:25::/64 {\n        AdvOnLink on;\n        AdvAutonomous on;\n    };\n};\n' | on r1 tee /etc/radvd.conf > /dev/null
on r1 tee /etc/nftables.conf > /dev/null << 'EOF'
flush ruleset
table inet filter {
    chain input { type filter hook input priority filter; policy drop; iif lo accept; ct state established,related accept; meta l4proto ipv6-icmp accept; iifname "lan" accept; }
    chain forward { type filter hook forward priority filter; policy drop; ct state established,related accept; iifname "lan" oifname "wan" accept; }
}
table ip nat {
    chain postrouting { type nat hook postrouting priority srcnat; policy accept; oifname "wan" masquerade; }
}
EOF
sudo systemctl enable --now nftables@r1 radvd@r1
sudo netlab restart
