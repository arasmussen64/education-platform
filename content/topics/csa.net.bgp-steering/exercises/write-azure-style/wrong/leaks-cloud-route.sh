# Wrong: both directions use dx1 and it's saved, but the route map that
# prepends over dx2 has no match line, so it lets out everything edge has:
# the office's network and the cloud's own 10.100.0.0/16, a route leak. The
# cloud drops its own network as a loop (its AS is in the path), so nothing
# changes on its side; edge still announces more than the office's prefix.
on edge vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 200
exit
route-map TO-DX2 permit 10
 set as-path prepend 65001 65001
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.20.2 route-map TO-DX2 out
end
write memory
EOF
