# Wrong: the cloud's traffic moves to dx1 by the other documented tool,
# more specific prefixes: the two halves of the office's network, /25s,
# announced over dx1 only, beat the /24 by longest match. It works, but the
# rule was to announce the office's 10.1.0.0/24 and nothing else, and every
# extra prefix counts against the provider's limit.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip route 10.1.0.0/25 lan
ip route 10.1.0.128/25 lan
ip prefix-list HALVES seq 5 permit 10.1.0.0/24
ip prefix-list HALVES seq 10 permit 10.1.0.0/25
ip prefix-list HALVES seq 15 permit 10.1.0.128/25
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 200
exit
route-map TO-DX1 permit 10
 match ip address prefix-list HALVES
exit
router bgp 65001
 address-family ipv4 unicast
  network 10.1.0.0/25
  network 10.1.0.128/25
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.30.2 route-map TO-DX1 out
end
write memory
EOF
