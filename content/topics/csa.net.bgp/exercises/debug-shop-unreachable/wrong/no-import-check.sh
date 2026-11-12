# Wrong: the route maps are fixed, but instead of announcing the shop's
# whole /24, the import check is switched off, so edge announces the /25
# it was told to, a prefix its routing table doesn't hold: half of the
# shop is still unreachable.
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
router bgp 65001
 no bgp network import-check
exit
end
write memory
EOF
# Long enough for a route map changed in use to reach the neighbours.
sleep 7
