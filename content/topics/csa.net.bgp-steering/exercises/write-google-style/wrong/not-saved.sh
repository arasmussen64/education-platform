# Wrong: everything is right, but never saved: a restart of FRR, or of
# depot, loses all of it.
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
 address-family ipv4 unicast
  neighbor 169.254.50.2 route-map TO-IC1 out
  neighbor 169.254.70.2 route-map TO-IC2 out
end
EOF
