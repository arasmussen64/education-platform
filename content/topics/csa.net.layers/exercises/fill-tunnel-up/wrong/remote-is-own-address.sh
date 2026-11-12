# Wrong: the tunnel's far end is r1's own address, so r1 wraps each packet
# and sends it to itself: the tunnel never reaches r2.
on r1 tee /etc/network/up > /dev/null << 'EOF'
ip addr add 10.0.1.1/24 dev eth0
ip addr add 203.0.113.1/24 dev wan
ip link add gre1 type gre local 203.0.113.1 remote 203.0.113.1 ttl 64
ip addr add 10.255.0.1/30 dev gre1
ip link set gre1 mtu 1476
ip link set gre1 up
ip route add 10.0.0.0/16 dev gre1
EOF
sudo netlab restart
