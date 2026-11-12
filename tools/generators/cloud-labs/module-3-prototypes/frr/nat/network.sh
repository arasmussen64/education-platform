#!/bin/bash
# Prototype: a private office behind a NAT gateway.
#   office 10.1.0.10, app 10.1.0.20 --lan-- gw [wan 198.51.100.2] --- [198.51.100.1] inet [203.0.113.1] --- srv 203.0.113.10, client 203.0.113.20
set -euo pipefail
for ns in office app gw inet srv client; do ip netns add "$ns"; ip -n "$ns" link set lo up; done
ip -n gw link add lan type bridge; ip -n gw link set lan up; ip -n gw addr add 10.1.0.1/24 dev lan
for h in office:10.1.0.10 app:10.1.0.20; do n=${h%%:*}; a=${h#*:}
  ip link add eth0 netns "$n" type veth peer name "p-$n" netns gw
  ip -n "$n" addr add "$a/24" dev eth0; ip -n "$n" link set eth0 up; ip -n "$n" route add default via 10.1.0.1
  ip -n gw link set "p-$n" master lan; ip -n gw link set "p-$n" up; done
ip -n inet link add pub type bridge; ip -n inet link set pub up; ip -n inet addr add 203.0.113.1/24 dev pub
for h in srv:203.0.113.10 client:203.0.113.20; do n=${h%%:*}; a=${h#*:}
  ip link add eth0 netns "$n" type veth peer name "p-$n" netns inet
  ip -n "$n" addr add "$a/24" dev eth0; ip -n "$n" link set eth0 up; ip -n "$n" route add default via 203.0.113.1
  ip -n inet link set "p-$n" master pub; ip -n inet link set "p-$n" up; done
ip link add wan netns gw type veth peer name isp netns inet
ip -n gw addr add 198.51.100.2/24 dev wan; ip -n gw link set wan up
ip -n inet addr add 198.51.100.1/24 dev isp; ip -n inet link set isp up
ip -n gw route add default via 198.51.100.1
# the internet has no route to 10.1.0.0/24: private addresses aren't routed there
for ns in office app gw inet srv client; do ip netns exec "$ns" sysctl -qw net.ipv4.conf.all.rp_filter=0 net.ipv4.conf.default.rp_filter=0 net.ipv4.ip_forward=0; done
for ns in gw inet; do ip netns exec "$ns" sysctl -qw net.ipv4.ip_forward=1; done
