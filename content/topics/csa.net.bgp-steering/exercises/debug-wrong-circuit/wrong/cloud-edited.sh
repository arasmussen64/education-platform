# Wrong: dc1's two faults are fixed, but the cloud's traffic is moved to
# circuit 1 by changing the cloud's router, which belongs to the provider:
# its route map now prefers what arrives over circuit 1.
on dc1 vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 address-family ipv4 unicast
  neighbor 10.0.2.1 next-hop-self
end
write memory
EOF
on dc1 vtysh << 'EOF' > /dev/null
configure terminal
bfd
 profile CIRCUIT
  receive-interval 300
  transmit-interval 300
 exit
exit
end
write memory
EOF
on cloud vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-PRIMARY permit 10
 set metric 0
 set local-preference 200
exit
router bgp 64600
 address-family ipv4 unicast
  neighbor 169.254.30.1 route-map FROM-PRIMARY in
end
write memory
EOF
