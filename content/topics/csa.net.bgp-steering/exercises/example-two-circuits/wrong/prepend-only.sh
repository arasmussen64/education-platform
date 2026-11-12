# Wrong: edge prefers dx1 for its own traffic, watches both sessions with
# BFD and saves, but tries to bring the cloud's traffic onto dx1 by
# prepending on dx2 alone. The cloud compares its local preference first,
# and gives dx2, in its associated Region, 200 against dx1's 150, so the
# cloud's traffic stays on dx2.
on edge vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 300
exit
route-map TO-DX2 permit 10
 match ip address prefix-list OURS
 set as-path prepend 65001 65001 65001
exit
router bgp 65001
 neighbor 169.254.30.2 bfd
 neighbor 169.254.20.2 bfd
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.20.2 route-map TO-DX2 out
end
write memory
EOF
