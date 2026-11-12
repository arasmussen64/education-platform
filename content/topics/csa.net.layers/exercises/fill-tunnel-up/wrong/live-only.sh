# Wrong: the tunnel is made with live commands only, and r1's network file
# still has its gaps. It works until the next boot, which builds r1 from
# its file again.
on r1 ip link add gre1 type gre local 203.0.113.1 remote 203.0.113.2 ttl 64
on r1 ip addr add 10.255.0.1/30 dev gre1
on r1 ip link set gre1 mtu 1476
on r1 ip link set gre1 up
on r1 ip route add 10.0.0.0/16 dev gre1
