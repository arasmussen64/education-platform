# Wrong: the tunnel is right, but the route for the cloud's addresses goes
# to r2 across the internet link instead of into the tunnel. The internet
# carries no private addresses: r2 drops what arrives that way.
on r1 tee /etc/network/up > /dev/null << 'EOF'
ip addr add 10.0.1.1/24 dev eth0
ip addr add 203.0.113.1/24 dev wan
ip link add gre1 type gre local 203.0.113.1 remote 203.0.113.2 ttl 64
ip addr add 10.255.0.1/30 dev gre1
ip link set gre1 mtu 1476
ip link set gre1 up
ip route add 10.0.0.0/16 via 203.0.113.2
EOF
sudo netlab restart
