# Wrong: instead of local preference, edge prepends its AS twice in what it
# sends ISP B. That changes how the internet reaches the shop, not which
# way the shop's own traffic leaves, so it still leaves through ISP B.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list OURS seq 5 permit 198.51.100.0/24
ip prefix-list NOT-OURS seq 5 deny 198.51.100.0/24 le 32
ip prefix-list NOT-OURS seq 10 permit 0.0.0.0/0 le 32
route-map TO-ISPS permit 10
 match ip address prefix-list OURS
exit
route-map TO-ISPB permit 10
 match ip address prefix-list OURS
 set as-path prepend 65001 65001
exit
route-map FROM-ISPA permit 10
 match ip address prefix-list NOT-OURS
exit
route-map FROM-ISPB permit 10
 match ip address prefix-list NOT-OURS
exit
router bgp 65001
 bgp router-id 198.51.100.1
 timers bgp 3 9
 neighbor 192.0.2.2 remote-as 65010
 neighbor 192.0.2.2 timers connect 5
 neighbor 192.0.2.6 remote-as 65020
 neighbor 192.0.2.6 timers connect 5
 address-family ipv4 unicast
  network 198.51.100.0/24
  neighbor 192.0.2.2 route-map FROM-ISPA in
  neighbor 192.0.2.2 route-map TO-ISPS out
  neighbor 192.0.2.6 route-map FROM-ISPB in
  neighbor 192.0.2.6 route-map TO-ISPB out
end
write memory
EOF
