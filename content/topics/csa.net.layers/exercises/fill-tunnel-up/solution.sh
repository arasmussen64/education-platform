# The reference answer: r1's network file with its four gaps filled. The
# tunnel runs from r1's address on the internet (203.0.113.1, on wan) to
# r2's (203.0.113.2); its MTU is the internet link's 1500 less GRE's 24
# bytes of headers (a 20-byte outer IPv4 header and a 4-byte GRE header);
# and the route for the cloud's addresses goes into the tunnel, gre1.
# "on r1 tee FILE << 'EOF'" writes the lines up to EOF into r1's FILE, as
# saving it in nano would. Then the network is built again from the files,
# as a reboot would, and the office tries the price list.
on r1 tee /etc/network/up > /dev/null << 'EOF'
# r1's network settings, run at every boot: the office's router.
ip addr add 10.0.1.1/24 dev eth0
ip addr add 203.0.113.1/24 dev wan
# The tunnel to the cloud's router, r2, across the internet: from r1's
# address on the internet to r2's. Replace each ___.
ip link add gre1 type gre local 203.0.113.1 remote 203.0.113.2 ttl 64
ip addr add 10.255.0.1/30 dev gre1
ip link set gre1 mtu 1476
ip link set gre1 up
# The cloud's networks are all inside 10.0.0.0/16.
ip route add 10.0.0.0/16 dev gre1
EOF
sudo netlab restart
on r1 ip -br addr show gre1
on office curl -s -o /dev/null -w '%{size_download} bytes\n' http://10.0.2.20/pricelist.csv
