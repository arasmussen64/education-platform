# Wrong: everything else is right, but the route map toward both ISPs
# refuses the three ISP routes edge has seen and lets everything else out,
# instead of letting out only the shop's prefix. Today only the shop's
# prefix leaves; the next route an ISP adds goes on to the other ISP.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list OURS seq 5 permit 198.51.100.0/24
ip prefix-list NOT-OURS seq 5 deny 198.51.100.0/24 le 32
ip prefix-list NOT-OURS seq 10 permit 0.0.0.0/0 le 32
ip prefix-list ISP-ROUTES seq 5 permit 10.10.0.0/16
ip prefix-list ISP-ROUTES seq 10 permit 10.20.0.0/16
ip prefix-list ISP-ROUTES seq 15 permit 203.0.113.0/24
route-map TO-ISPS deny 10
 match ip address prefix-list ISP-ROUTES
exit
route-map TO-ISPS permit 20
exit
route-map FROM-ISPA permit 10
 match ip address prefix-list NOT-OURS
 set local-preference 200
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
  neighbor 192.0.2.6 route-map TO-ISPS out
end
write memory
EOF
