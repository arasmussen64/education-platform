# Wrong: all three fixes are right, but eBGP's rule that a session needs a
# policy is switched off on dc2 as well, so a session added later without
# route maps would send and accept everything.
on dc2 vtysh << 'EOF' > /dev/null
configure terminal
route-map TO-CLOUD permit 10
 no set community
 set as-path prepend 65001 65001
end
write memory
EOF
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
on dc2 vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 no bgp ebgp-requires-policy
end
write memory
EOF
