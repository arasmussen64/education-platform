# Wrong: the import route map has no match line, so it permits
# everything the cloud sends: its private network and a default route
# come in with its web servers' network.
on edge vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-CLOUD permit 10
exit
route-map TO-CLOUD permit 10
 match ip address prefix-list OURS
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
