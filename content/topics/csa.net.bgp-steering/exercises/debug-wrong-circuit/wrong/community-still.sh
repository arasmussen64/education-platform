# Wrong: dc1's next hop and BFD are fixed, but dc2 still tags its routes
# with AWS's low-preference community and doesn't prepend. This cloud, like
# Microsoft's, ignores every community you send, so its two paths stay equal
# and it shares its traffic for the data centre over both circuits.
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
