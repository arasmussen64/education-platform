# Wrong: both directions use ic2 and it's saved, but the two route maps
# that set the MED have no match line, so they let out everything depot
# has: the depot's network and the cloud's own 10.60.0.0/16, a route leak.
# The cloud drops its own network as a loop (its AS is in the path), so
# nothing changes on its side; depot still announces more than the depot's
# prefix.
on depot vtysh << 'EOF' > /dev/null
configure terminal
route-map TO-IC1 permit 10
 set metric 200
exit
route-map TO-IC2 permit 10
 set metric 100
exit
router bgp 65002
 address-family ipv4 unicast
  neighbor 169.254.50.2 route-map TO-IC1 out
  neighbor 169.254.70.2 route-map TO-IC2 out
end
write memory
EOF
