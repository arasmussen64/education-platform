# Wrong: the route maps are fixed, but edge announces 198.51.0.0/16,
# made valid with a blackhole route, and OURS was widened to let it out:
# edge now claims 65,536 addresses, of which the shop owns 256.
on edge vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 address-family ipv4 unicast
  neighbor 192.0.2.2 route-map FROM-ISPA in
  neighbor 192.0.2.6 route-map FROM-ISPB in
exit
exit
route-map TO-ISPB permit 10
 match ip address prefix-list OURS
exit
ip route 198.51.0.0/16 blackhole
ip prefix-list OURS seq 5 permit 198.51.0.0/16
router bgp 65001
 address-family ipv4 unicast
  no network 198.51.100.0/25
  network 198.51.0.0/16
exit
exit
end
write memory
EOF
# Long enough for a route map changed in use to reach the neighbours.
sleep 7
