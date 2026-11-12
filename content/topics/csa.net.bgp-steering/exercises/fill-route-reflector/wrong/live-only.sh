# Wrong: the four lines were typed into core's and dc2's consoles instead,
# and never saved: everything works today, and both files still have their
# gaps, so the next restart of FRR (or of the routers) loses them.
on core vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 address-family ipv4 unicast
  neighbor 10.0.1.2 route-reflector-client
  neighbor 10.0.2.2 route-reflector-client
  neighbor 10.0.3.2 route-reflector-client
end
EOF
on dc2 vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 address-family ipv4 unicast
  neighbor 10.0.3.1 next-hop-self
end
EOF
