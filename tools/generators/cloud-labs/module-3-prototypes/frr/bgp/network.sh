#!/bin/bash
# Prototype: the BGP lab's network, made at boot.
#
#   office 198.51.100.10 -- lan [edge AS65001] ispa -- shop [ispa AS65010] cloud -- ispa [cloud AS65100] web -- web 203.0.113.10
#                                              ispb -- shop [ispb AS65020] cloud -- ispb
set -euo pipefail
for ns in office edge ispa ispb cloud web; do
  ip netns add "$ns"
  ip -n "$ns" link set lo up
done
# link NS1 IF1 ADDR1 NS2 IF2 ADDR2
link() {
  ip link add "$2" netns "$1" type veth peer name "$5" netns "$4"
  ip -n "$1" addr add "$3" dev "$2"; ip -n "$1" link set "$2" up
  ip -n "$4" addr add "$6" dev "$5"; ip -n "$4" link set "$5" up
}
link office eth0 198.51.100.10/24  edge lan 198.51.100.1/24
link edge ispa 192.0.2.1/30       ispa shop 192.0.2.2/30
link edge ispb 192.0.2.5/30       ispb shop 192.0.2.6/30
link ispa cloud 192.0.2.9/30      cloud ispa 192.0.2.10/30
link ispb cloud 192.0.2.13/30     cloud ispb 192.0.2.14/30
link cloud web 203.0.113.1/24      web eth0 203.0.113.10/24
ip -n office route add default via 198.51.100.1
ip -n web route add default via 203.0.113.1
# Every machine's kernel settings are set here, not inherited, so Docker
# Desktop and a CI runner agree: routers forward, nobody filters by reverse path.
for ns in office edge ispa ispb cloud web; do
  ip netns exec "$ns" sysctl -qw net.ipv4.conf.all.rp_filter=0 net.ipv4.conf.default.rp_filter=0
done
