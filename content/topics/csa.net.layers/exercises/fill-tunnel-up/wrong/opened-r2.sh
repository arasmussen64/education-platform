# Wrong: the route goes across the internet link, and r2's firewall is
# opened so that it lets that traffic in. It works, but r2 isn't the
# learner's to change. (The lab machine's path to r2's file: sed -i
# can't replace a machine's file that sits straight in /etc from inside.)
on r1 tee /etc/network/up > /dev/null << 'EOF'
ip addr add 10.0.1.1/24 dev eth0
ip addr add 203.0.113.1/24 dev wan
ip link add gre1 type gre local 203.0.113.1 remote 203.0.113.2 ttl 64
ip addr add 10.255.0.1/30 dev gre1
ip link set gre1 mtu 1476
ip link set gre1 up
ip route add 10.0.0.0/16 via 203.0.113.2
EOF
sudo sed -i 's/iifname "wan" drop/iifname "wan" accept/' /etc/netns/r2/nftables.conf
sudo netlab restart
