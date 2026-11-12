#!/bin/bash
# Prototype: three sites in a triangle of routers.
#   office 10.1.0.10 --lan-- r1 ==r2== r2 --lan-- store 10.2.0.10
#                            \       //
#                             r3 -- r3 --lan-- dc 10.3.0.10
set -euo pipefail
for ns in office store dc r1 r2 r3; do ip netns add "$ns"; ip -n "$ns" link set lo up; done
link() { ip link add "$2" netns "$1" type veth peer name "$5" netns "$4"
  ip -n "$1" addr add "$3" dev "$2"; ip -n "$1" link set "$2" up
  ip -n "$4" addr add "$6" dev "$5"; ip -n "$4" link set "$5" up; }
link office eth0 10.1.0.10/24  r1 lan 10.1.0.1/24
link store eth0 10.2.0.10/24   r2 lan 10.2.0.1/24
link dc eth0 10.3.0.10/24      r3 lan 10.3.0.1/24
link r1 r2 10.0.12.1/30        r2 r1 10.0.12.2/30
link r1 r3 10.0.13.1/30        r3 r1 10.0.13.2/30
link r2 r3 10.0.23.1/30        r3 r2 10.0.23.2/30
ip -n office route add default via 10.1.0.1
ip -n store route add default via 10.2.0.1
ip -n dc route add default via 10.3.0.1
for ns in office store dc; do ip netns exec "$ns" sysctl -qw net.ipv4.ip_forward=0 net.ipv4.conf.all.rp_filter=0 net.ipv4.conf.default.rp_filter=0; done
for ns in r1 r2 r3; do ip netns exec "$ns" sysctl -qw net.ipv4.ip_forward=1 net.ipv4.conf.all.rp_filter=0 net.ipv4.conf.default.rp_filter=0; done
