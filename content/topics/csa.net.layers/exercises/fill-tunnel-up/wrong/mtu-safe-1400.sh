# Wrong: a "safe" round MTU of 1400. Nothing is fragmented, but every
# full-size packet carries 76 bytes less than the path allows.
on r1 tee /etc/network/up > /dev/null << 'EOF'
ip addr add 10.0.1.1/24 dev eth0
ip addr add 203.0.113.1/24 dev wan
ip link add gre1 type gre local 203.0.113.1 remote 203.0.113.2 ttl 64
ip addr add 10.255.0.1/30 dev gre1
ip link set gre1 mtu 1400
ip link set gre1 up
ip route add 10.0.0.0/16 dev gre1
EOF
sudo netlab restart
