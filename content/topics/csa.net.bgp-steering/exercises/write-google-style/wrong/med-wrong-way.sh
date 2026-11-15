# Wrong: the cloud's two numbers read as if the higher were the better, as
# local preference is. The cloud's 200 is on ic1, so depot asks for the
# cloud's traffic over ic1 by sending the lower MED there. The cloud does
# what the MED asks and sends over ic1, while depot's own traffic still
# leaves over ic2, which the cloud's MED of 100 names: each conversation
# goes out one circuit and comes back the other.
on depot vtysh << 'EOF' > /dev/null
configure terminal
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
  neighbor 169.254.50.2 route-map TO-IC1 out
  neighbor 169.254.70.2 route-map TO-IC2 out
end
write memory
EOF
