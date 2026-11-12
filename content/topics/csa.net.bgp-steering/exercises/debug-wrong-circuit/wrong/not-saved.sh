# Wrong: all three fixes are right, but none is saved: a restart of FRR,
# or of the routers, loses them.
on dc2 vtysh << 'EOF' > /dev/null
configure terminal
route-map TO-CLOUD permit 10
 no set community
 set as-path prepend 65001 65001
end
EOF
on dc1 vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 address-family ipv4 unicast
  neighbor 10.0.2.1 next-hop-self
end
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
EOF
