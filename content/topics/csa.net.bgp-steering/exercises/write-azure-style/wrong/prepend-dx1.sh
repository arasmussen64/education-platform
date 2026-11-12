# Wrong: the prepend goes on the wrong circuit. edge prefers dx1 for its
# own traffic, but makes the path over dx1 longer, so the cloud sends all its
# traffic over dx2.
on edge vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 200
exit
route-map TO-DX1 permit 10
 match ip address prefix-list OURS
 set as-path prepend 65001 65001
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.30.2 route-map TO-DX1 out
end
write memory
EOF
