# Wrong: both directions use dx1 and the work is saved, but edge's sessions
# aren't watched by BFD, so when dx1 dies silently BGP notices only when its
# hold time runs out, about 9 seconds in the lab (90 on AWS's side by
# default).
on edge vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 300
exit
route-map TO-DX1 permit 10
 match ip address prefix-list OURS
 set community 7224:7300
exit
route-map TO-DX2 permit 10
 match ip address prefix-list OURS
 set community 7224:7100
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.30.2 route-map TO-DX1 out
  neighbor 169.254.20.2 route-map TO-DX2 out
end
write memory
EOF
