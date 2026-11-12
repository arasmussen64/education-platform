# Wrong: the cloud's traffic moves to circuit 1 by more specific prefixes,
# the data centre's two halves (/23s) announced by dc1 only, which beat the
# summary by longest match. It works, but the rule was to announce the
# summary and nothing else.
on dc2 vtysh << 'EOF' > /dev/null
configure terminal
route-map TO-CLOUD permit 10
 no set community
end
write memory
EOF
on dc1 vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list DC seq 10 permit 10.1.0.0/23
ip prefix-list DC seq 15 permit 10.1.2.0/23
router bgp 65001
 address-family ipv4 unicast
  aggregate-address 10.1.0.0/23
  aggregate-address 10.1.2.0/23
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
