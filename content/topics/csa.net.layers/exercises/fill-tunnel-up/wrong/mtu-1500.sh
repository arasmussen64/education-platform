# Wrong: the tunnel's MTU is the internet link's own, 1500, which leaves no
# room for GRE's 24 bytes of headers: a full-size packet into the tunnel
# becomes 1524 bytes on a 1500-byte link.
on r1 tee /etc/network/up > /dev/null << 'EOF'
ip addr add 10.0.1.1/24 dev eth0
ip addr add 203.0.113.1/24 dev wan
ip link add gre1 type gre local 203.0.113.1 remote 203.0.113.2 ttl 64
ip addr add 10.255.0.1/30 dev gre1
ip link set gre1 mtu 1500
ip link set gre1 up
ip route add 10.0.0.0/16 dev gre1
EOF
sudo netlab restart
