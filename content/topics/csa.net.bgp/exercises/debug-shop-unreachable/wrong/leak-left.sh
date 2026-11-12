# Wrong: the route maps and the announcement are fixed, but the route
# map toward ISP B still permits everything, so edge still passes ISP
# A's routes on to ISP B.
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
