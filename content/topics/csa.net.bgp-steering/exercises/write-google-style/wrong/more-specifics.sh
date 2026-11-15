# Wrong: the cloud's traffic moves to ic2 by more specific prefixes: the
# two halves of the depot's network, /25s, announced over ic2 only, beat
# the /24 by longest match. It works on every cloud, but the rule was to
# announce the depot's 10.2.0.0/24 and nothing else, and to let the MED
# decide.
on depot vtysh << 'EOF' > /dev/null
configure terminal
ip route 10.2.0.0/25 lan
ip route 10.2.0.128/25 lan
ip prefix-list HALVES seq 5 permit 10.2.0.0/24
ip prefix-list HALVES seq 10 permit 10.2.0.0/25
ip prefix-list HALVES seq 15 permit 10.2.0.128/25
route-map TO-IC2 permit 10
 match ip address prefix-list HALVES
exit
router bgp 65002
 address-family ipv4 unicast
  network 10.2.0.0/25
  network 10.2.0.128/25
  neighbor 169.254.70.2 route-map TO-IC2 out
end
write memory
EOF
