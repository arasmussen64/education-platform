# Wrong: the session has no route maps, and eBGP's policy requirement is
# switched off instead, so it sends and accepts everything.
on edge vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 no bgp ebgp-requires-policy
 neighbor 169.254.30.2 remote-as 65100
 neighbor 169.254.30.2 timers connect 5
end
write memory
EOF
