# Wrong: the community is gone from dc2, but the prepend went on dc1, the
# primary: the path over circuit 1 is now the longer one, so the cloud sends
# all its traffic over circuit 2.
on dc2 vtysh << 'EOF' > /dev/null
configure terminal
route-map TO-CLOUD permit 10
 no set community
end
write memory
EOF
on dc1 vtysh << 'EOF' > /dev/null
configure terminal
route-map TO-CLOUD permit 10
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
