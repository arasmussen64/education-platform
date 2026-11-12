#!/bin/bash
# Prototype: the shop's data centre (edge, AS 65001) joined to a cloud (AS 64512) by two circuits.
#   office 10.1.0.10 --lan-- edge ==dx1 169.254.10.0/30== cloud --vpc-- app 10.100.0.10
#                                \==dx2 169.254.20.0/30==/
set -euo pipefail
for ns in office edge cloud app; do ip netns add "$ns"; ip -n "$ns" link set lo up; done
link() { ip link add "$2" netns "$1" type veth peer name "$5" netns "$4"
  ip -n "$1" addr add "$3" dev "$2"; ip -n "$1" link set "$2" up
  ip -n "$4" addr add "$6" dev "$5"; ip -n "$4" link set "$5" up; }
link office eth0 10.1.0.10/24 edge lan 10.1.0.1/24
link edge dx1 169.254.10.1/30 cloud dx1 169.254.10.2/30
link edge dx2 169.254.20.1/30 cloud dx2 169.254.20.2/30
link cloud vpc 10.100.0.1/16 app eth0 10.100.0.10/16
ip -n office route add default via 10.1.0.1; ip -n app route add default via 10.100.0.1
for ns in office app; do ip netns exec $ns sysctl -qw net.ipv4.ip_forward=0 net.ipv4.conf.all.rp_filter=0 net.ipv4.conf.default.rp_filter=0; done
for ns in edge cloud; do ip netns exec $ns sysctl -qw net.ipv4.ip_forward=1 net.ipv4.conf.all.rp_filter=0 net.ipv4.conf.default.rp_filter=0; done
