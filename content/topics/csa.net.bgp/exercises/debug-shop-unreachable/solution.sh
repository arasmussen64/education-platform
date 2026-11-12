# The reference: three changes in edge's console, then saved.
#   1. ISP A's routes go through FROM-ISPA, the route map that gives them
#      local preference 200, and ISP B's through FROM-ISPB: the two had been
#      swapped, so ISP B's routes carried the 200 and won.
#   2. edge announces the shop's whole network, 198.51.100.0/24. The /25 it
#      had been told to announce isn't in its routing table (only the
#      connected /24 is), so FRR announced nothing at all, and the internet
#      had no route back to the shop.
#   3. The route map toward ISP B gets back its match on OURS: without it,
#      it permitted everything, and edge passed ISP A's routes to ISP B.
# "on edge vtysh << 'EOF'" sends the lines up to EOF to edge's console, as
# if they were typed at the edge# prompt.
on edge vtysh << 'EOF'
configure terminal
router bgp 65001
 address-family ipv4 unicast
  no network 198.51.100.0/25
  network 198.51.100.0/24
  neighbor 192.0.2.2 route-map FROM-ISPA in
  neighbor 192.0.2.6 route-map FROM-ISPB in
exit
exit
route-map TO-ISPB permit 10
 match ip address prefix-list OURS
end
write memory
EOF
# Look, once it has all arrived: a route map changed while in use takes
# about 5 seconds to reach the neighbour, so wait until ISP B has exactly
# one route from edge (one line starting "*>"), and until edge's kernel
# sends the cloud's traffic to ISP A.
for _ in $(seq 1 30); do
  [ "$(looking-glass ispb 'show bgp ipv4 unicast neighbors 192.0.2.5 routes' | grep -c '^\*>')" = 1 ] &&
    on edge ip route get 203.0.113.10 | grep 'via 192.0.2.2' > /dev/null && break
  sleep 1
done
looking-glass ispb 'show bgp ipv4 unicast neighbors 192.0.2.5 routes'
on edge ip route get 203.0.113.10
on web curl -sS -m 3 http://198.51.100.200/
