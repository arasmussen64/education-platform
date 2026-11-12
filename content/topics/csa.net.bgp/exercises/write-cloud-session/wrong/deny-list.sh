# Wrong: the import policy refuses the two things the cloud offers today,
# the default route and its private network, and permits the rest, so
# whatever the cloud adds next comes straight in.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list NOT-CLOUD-EXTRAS seq 5 deny 0.0.0.0/0
ip prefix-list NOT-CLOUD-EXTRAS seq 10 deny 10.200.0.0/16
ip prefix-list NOT-CLOUD-EXTRAS seq 15 permit 0.0.0.0/0 le 32
route-map FROM-CLOUD permit 10
 match ip address prefix-list NOT-CLOUD-EXTRAS
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
