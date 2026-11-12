# Wrong: dc2 prepends and dc1 sets its next hop, but dc1's BFD profile
# still asks for a packet every 3000 ms, so a silent failure of circuit 1
# takes 3000 x 3 = 9 seconds to notice.
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
