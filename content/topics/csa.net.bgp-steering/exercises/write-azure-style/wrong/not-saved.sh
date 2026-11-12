# Wrong: everything is right, but never saved: a restart of FRR, or of
# edge, loses all of it.
on edge vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 200
exit
route-map TO-DX2 permit 10
 match ip address prefix-list OURS
 set as-path prepend 65001 65001
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.20.2 route-map TO-DX2 out
end
EOF
