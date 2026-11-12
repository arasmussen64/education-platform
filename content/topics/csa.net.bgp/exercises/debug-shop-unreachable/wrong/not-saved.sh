# Wrong: all three faults are fixed in edge's console, and never saved:
# the next restart of FRR, or of edge, brings all three back.
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
route-map TO-ISPB permit 10
 match ip address prefix-list OURS
exit
end
EOF
# Long enough for a route map changed in use to reach the neighbours.
sleep 7
