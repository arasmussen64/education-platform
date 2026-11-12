# Wrong: the export route map has no match line, so edge sends the cloud
# everything it knows, the ISPs' routes included: the shop offers itself
# to the cloud as a path to the rest of the internet.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list CLOUD-WEB seq 5 permit 203.0.113.0/24
route-map FROM-CLOUD permit 10
 match ip address prefix-list CLOUD-WEB
exit
route-map TO-CLOUD permit 10
exit
router bgp 65001
 neighbor 169.254.30.2 remote-as 65100
 neighbor 169.254.30.2 timers connect 5
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-CLOUD in
  neighbor 169.254.30.2 route-map TO-CLOUD out
end
write memory
EOF
