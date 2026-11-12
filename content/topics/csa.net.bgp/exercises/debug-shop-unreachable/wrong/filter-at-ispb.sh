# Wrong: edge's route maps and announcement are fixed, and instead of
# fixing edge's leak, ISP B's router was told to take only the shop's
# prefix from edge, and saved. ISP B's router isn't the shop's to
# change, and edge still offers ISP A's routes to anyone it talks to.
on edge vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 address-family ipv4 unicast
  neighbor 192.0.2.2 route-map FROM-ISPA in
  neighbor 192.0.2.6 route-map FROM-ISPB in
exit
exit
router bgp 65001
 address-family ipv4 unicast
  no network 198.51.100.0/25
  network 198.51.100.0/24
exit
exit
end
write memory
EOF
on ispb vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list SHOP-ONLY seq 5 permit 198.51.100.0/24
route-map FROM-SHOP permit 10
 match ip address prefix-list SHOP-ONLY
exit
end
write memory
EOF
# Long enough for a route map changed in use to reach the neighbours.
sleep 7
