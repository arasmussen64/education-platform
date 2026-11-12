#!/bin/bash
# IPv6 prototype v2: h1, h2 -- (bridge) r1 --1500-- isp ==1400== core --1500-- web.  Dual stack.
set -eu
for m in h1 h2 r1 isp core web; do ip netns add $m; ip -n $m link set lo up; done
link() { ip link add tmpa type veth peer name tmpb; ip link set tmpa netns $1 name $2; ip link set tmpb netns $3 name $4; ip -n $1 link set $2 up; ip -n $3 link set $4 up; }
ip -n r1 link add lan type bridge; ip -n r1 link set lan up
link h1 eth0 r1 p-h1; ip -n r1 link set p-h1 master lan
link h2 eth0 r1 p-h2; ip -n r1 link set p-h2 master lan
link r1 wan isp cust
link isp core core edge
link core srv web eth0
ip -n isp link set core mtu 1400; ip -n core link set edge mtu 1400
ip -n r1 addr add 192.168.10.1/24 dev lan
for h in h1:11 h2:12; do IFS=: read n o <<< $h; ip -n $n addr add 192.168.10.$o/24 dev eth0; ip -n $n route add default via 192.168.10.1; done
ip -n r1 addr add 198.51.100.2/30 dev wan; ip -n isp addr add 198.51.100.1/30 dev cust; ip -n r1 route add default via 198.51.100.1
ip -n isp addr add 198.51.100.5/30 dev core; ip -n core addr add 198.51.100.6/30 dev edge
ip -n isp route add default via 198.51.100.6; ip -n core route add 198.51.100.0/30 via 198.51.100.5
ip -n core addr add 203.0.113.1/24 dev srv; ip -n web addr add 203.0.113.80/24 dev eth0; ip -n web route add default via 203.0.113.1
ip -n r1 addr add 2001:db8:42:a::1/64 dev lan
ip -n r1 addr add 2001:db8:ffff:1::2/64 dev wan; ip -n isp addr add 2001:db8:ffff:1::1/64 dev cust
ip -n r1 route add default via 2001:db8:ffff:1::1
ip -n isp addr add 2001:db8:ffff:2::1/64 dev core; ip -n core addr add 2001:db8:ffff:2::2/64 dev edge
ip -n isp route add 2001:db8:42::/48 via 2001:db8:ffff:1::2; ip -n isp route add default via 2001:db8:ffff:2::2
ip -n core route add 2001:db8:42::/48 via 2001:db8:ffff:2::1; ip -n core route add 2001:db8:ffff:1::/64 via 2001:db8:ffff:2::1
ip -n core addr add 2001:db8:80::1/64 dev srv; ip -n web addr add 2001:db8:80::80/64 dev eth0; ip -n web route add default via 2001:db8:80::1
ip -n web route add local 2001:db8:80::1000/116 dev lo
for m in isp core; do ip netns exec $m sysctl -qw net.ipv4.ip_forward=1 net.ipv6.conf.all.forwarding=1; done
ip netns exec r1 sysctl -qw net.ipv4.ip_forward=1 net.ipv6.conf.all.forwarding=1
