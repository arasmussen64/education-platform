# Wrong: the MEDs are right and saved, but eBGP's policy requirement was
# switched off on the way, so a session with no route map would now accept
# and send everything.
on depot vtysh << 'EOF' > /dev/null
configure terminal
route-map TO-IC1 permit 10
 match ip address prefix-list OURS
 set metric 200
exit
route-map TO-IC2 permit 10
 match ip address prefix-list OURS
 set metric 100
exit
router bgp 65002
 no bgp ebgp-requires-policy
 address-family ipv4 unicast
  neighbor 169.254.50.2 route-map TO-IC1 out
  neighbor 169.254.70.2 route-map TO-IC2 out
end
write memory
EOF
