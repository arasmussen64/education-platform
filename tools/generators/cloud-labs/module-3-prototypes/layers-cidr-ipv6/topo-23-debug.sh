#!/bin/bash
# Prototype of topic 23's debug topology. Machines are network namespaces.
#  office 10.0.1.10 -- r1 10.0.1.1 | wan 203.0.113.1 ==GRE 10.255.0.1/30== r2 | wan 203.0.113.2, lan 10.0.2.1, prn 10.0.3.1
#  web 10.0.2.20, files 10.0.2.30 on r2's lan (a bridge in r2), printer 10.0.3.5
set -eu
for m in office r1 r2 web files printer; do ip netns add $m; ip -n $m link set lo up; done
link() { # link A IFA B IFB
  ip link add tmpa type veth peer name tmpb
  ip link set tmpa netns $1 name $2; ip link set tmpb netns $3 name $4
  ip -n $1 link set $2 up; ip -n $3 link set $4 up; }
link office eth0 r1 eth0
link r1 wan r2 wan
link printer eth0 r2 prn
# r2's LAN: a bridge with web and files on it
ip -n r2 link add lan type bridge; ip -n r2 link set lan up
link web eth0 r2 p-web; ip -n r2 link set p-web master lan
link files eth0 r2 p-files; ip -n r2 link set p-files master lan
ip -n office addr add 10.0.1.10/24 dev eth0; ip -n office route add default via 10.0.1.1
ip -n r1 addr add 10.0.1.1/24 dev eth0; ip -n r1 addr add 203.0.113.1/24 dev wan
ip -n r2 addr add 203.0.113.2/24 dev wan; ip -n r2 addr add 10.0.2.1/24 dev lan; ip -n r2 addr add 10.0.3.1/24 dev prn
ip -n web addr add 10.0.2.20/24 dev eth0; ip -n web route add default via 10.0.2.1
ip -n files addr add 10.0.2.30/24 dev eth0; ip -n files route add default via 10.0.2.1
ip -n printer addr add 10.0.3.5/24 dev eth0; ip -n printer route add default via 10.0.3.1
ip -n r1 link add gre1 type gre local 203.0.113.1 remote 203.0.113.2 ttl 64
ip -n r2 link add gre1 type gre local 203.0.113.2 remote 203.0.113.1 ttl 64
ip -n r1 addr add 10.255.0.1/30 dev gre1; ip -n r2 addr add 10.255.0.2/30 dev gre1
ip -n r1 link set gre1 up; ip -n r2 link set gre1 up
ip -n r1 route add 10.0.0.0/16 dev gre1        # all the shop's networks are across the tunnel
ip -n r2 route add default dev gre1            # forced tunnelling: everything leaves through the office
for m in r1 r2; do ip netns exec $m sysctl -qw net.ipv4.ip_forward=1; done
