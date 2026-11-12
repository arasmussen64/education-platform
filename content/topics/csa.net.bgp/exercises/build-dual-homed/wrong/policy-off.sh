# Wrong: instead of route maps, eBGP's policy requirement is switched off,
# so edge sends everything and takes everything: the leak and the stolen
# addresses are both back.
on edge vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 bgp router-id 198.51.100.1
 no bgp ebgp-requires-policy
 timers bgp 3 9
 neighbor 192.0.2.2 remote-as 65010
 neighbor 192.0.2.2 timers connect 5
 neighbor 192.0.2.6 remote-as 65020
 neighbor 192.0.2.6 timers connect 5
 address-family ipv4 unicast
  network 198.51.100.0/24
end
write memory
EOF
