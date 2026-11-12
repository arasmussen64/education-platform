# Wrong: the announcement and the leak are fixed, but the two inbound
# route maps are still the wrong way round, so ISP B's routes carry the
# local preference of 200 and the shop's traffic leaves through ISP B.
on edge vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 address-family ipv4 unicast
  no network 198.51.100.0/25
  network 198.51.100.0/24
exit
exit
route-map TO-ISPB permit 10
 match ip address prefix-list OURS
exit
end
write memory
EOF
# Long enough for a route map changed in use to reach the neighbours.
sleep 7
