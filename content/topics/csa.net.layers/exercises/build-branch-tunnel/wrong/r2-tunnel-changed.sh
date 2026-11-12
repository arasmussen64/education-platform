# Wrong: r3 is right, but r2's end of the tunnel was changed too (its MTU
# line taken out, to leave both ends to the kernel), and r2 isn't the
# learner's to change.
on r3 tee /etc/network/up > /dev/null << 'EOF'
ip addr add 10.0.5.1/24 dev eth0
ip addr add 198.51.100.6/30 dev wan
ip route add default via 198.51.100.5
ip link add gre1 type gre local 198.51.100.6 remote 203.0.113.2 ttl 64
ip addr add 10.255.1.2/30 dev gre1
ip link set gre1 mtu 1376
ip link set gre1 up
ip route add 10.0.2.0/24 dev gre1
EOF
on r3 tee /etc/nftables.conf > /dev/null << 'EOF'
flush ruleset
table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;
        iif lo accept
        ct state established,related accept
        iifname "eth0" accept
        iifname "wan" ip saddr 203.0.113.2 ip protocol gre accept
    }
    chain forward {
        type filter hook forward priority filter; policy drop;
        ct state established,related accept
        iifname { "eth0", "gre1" } accept
    }
}
EOF
sudo systemctl enable nftables@r3
sudo sed -i '/ip link set gre-br mtu/d' /etc/netns/r2/network/up
sudo netlab restart
mkdir -p ~/build
on r3 timeout 5 tcpdump -nn -c 1 -i wan ip proto 47 > ~/build/tunnel.txt &
sleep 1; on branch ping -c 1 10.0.2.20 > /dev/null; wait
