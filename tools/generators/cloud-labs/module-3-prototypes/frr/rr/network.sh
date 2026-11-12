#!/bin/bash
# Prototype: AS 65001 has three routers; only r1 touches the cloud (AS 64512).
#   cloud(64512) --dx-- r1 --- r2 --- r3 --lan-- office 10.1.30.10
set -euo pipefail
for ns in cloud r1 r2 r3 office app; do ip netns add "$ns"; ip -n "$ns" link set lo up; done
link() { ip link add "$2" netns "$1" type veth peer name "$5" netns "$4"
  ip -n "$1" addr add "$3" dev "$2"; ip -n "$1" link set "$2" up
  ip -n "$4" addr add "$6" dev "$5"; ip -n "$4" link set "$5" up; }
link cloud dx 169.254.10.2/30 r1 dx 169.254.10.1/30
link r1 r2 10.0.12.1/30 r2 r1 10.0.12.2/30
link r2 r3 10.0.23.1/30 r3 r2 10.0.23.2/30
link r3 lan 10.1.30.1/24 office eth0 10.1.30.10/24
link cloud vpc 10.100.0.1/16 app eth0 10.100.0.10/16
ip -n office route add default via 10.1.30.1; ip -n app route add default via 10.100.0.1
for ns in office app; do ip netns exec $ns sysctl -qw net.ipv4.ip_forward=0; done
for ns in cloud r1 r2 r3 office app; do ip netns exec $ns sysctl -qw net.ipv4.conf.all.rp_filter=0 net.ipv4.conf.default.rp_filter=0; done
for ns in cloud r1 r2 r3; do ip netns exec $ns sysctl -qw net.ipv4.ip_forward=1; done
