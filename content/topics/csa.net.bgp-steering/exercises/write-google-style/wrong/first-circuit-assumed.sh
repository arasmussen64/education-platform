# Wrong: ic1 taken for the primary because it is the first, without reading
# what the cloud announces. depot prefers ic1 for its own traffic by local
# preference, which is compared long before MED and so overrides the
# cloud's 100 on ic2, and sends the higher MED over ic2. Both directions
# agree, on the circuit the cloud team made the backup.
on depot vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-IC1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 200
exit
route-map TO-IC1 permit 10
 match ip address prefix-list OURS
 set metric 100
exit
route-map TO-IC2 permit 10
 match ip address prefix-list OURS
 set metric 200
exit
router bgp 65002
 address-family ipv4 unicast
  neighbor 169.254.50.2 route-map FROM-IC1 in
  neighbor 169.254.50.2 route-map TO-IC1 out
  neighbor 169.254.70.2 route-map TO-IC2 out
end
write memory
EOF
