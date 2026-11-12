# Wrong: the route maps and the leak are fixed, but edge is still told
# to announce 198.51.100.0/25, which isn't in its routing table, so it
# announces nothing and the internet has no way back to the shop.
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
end
write memory
EOF
# Long enough for a route map changed in use to reach the neighbours.
sleep 7
