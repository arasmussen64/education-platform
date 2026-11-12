on edge vtysh -c 'show bgp summary'
on office traceroute -n -w 1 -q 1 -m 4 203.0.113.10
on edge vtysh << 'EOF'
configure terminal
router bgp 65001
 bgp router-id 198.51.100.1
 timers bgp 3 9
 neighbor 192.0.2.2 remote-as 65010
 neighbor 192.0.2.2 timers connect 5
end
EOF
on edge vtysh -c 'show bgp summary'
sleep 6
on edge vtysh -c 'show bgp summary'
on edge vtysh -c 'show bgp neighbors 192.0.2.2' | grep policy
on edge vtysh << 'EOF'
configure terminal
route-map ALLOW permit 10
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 192.0.2.2 route-map ALLOW in
  neighbor 192.0.2.2 route-map ALLOW out
end
EOF
sleep 3
on edge vtysh -c 'show bgp ipv4 unicast'
on edge vtysh -c 'show ip route bgp'
on office traceroute -n -w 1 -q 1 -m 5 203.0.113.10
looking-glass cloud 'show bgp ipv4 unicast 198.51.100.0/24'
on edge vtysh << 'EOF'
configure terminal
router bgp 65001
 address-family ipv4 unicast
  network 198.51.100.0/24
end
EOF
looking-glass ispa 'show bgp ipv4 unicast neighbors 192.0.2.1 routes'
on office curl -sS -m 3 http://203.0.113.10/
on edge vtysh << 'EOF'
configure terminal
router bgp 65001
 neighbor 192.0.2.6 remote-as 65020
 neighbor 192.0.2.6 timers connect 5
 address-family ipv4 unicast
  neighbor 192.0.2.6 route-map ALLOW in
  neighbor 192.0.2.6 route-map ALLOW out
end
EOF
sleep 6
looking-glass ispb 'show bgp ipv4 unicast neighbors 192.0.2.5 routes'
on edge vtysh -c 'show bgp ipv4 unicast 198.51.100.128/25'
on edge ip route get 198.51.100.200
on web traceroute -n -w 1 -q 1 -m 6 198.51.100.200
on edge vtysh << 'EOF'
configure terminal
ip prefix-list OURS seq 5 permit 198.51.100.0/24
route-map TO-ISPS permit 10
 match ip address prefix-list OURS
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 192.0.2.2 route-map TO-ISPS out
  neighbor 192.0.2.6 route-map TO-ISPS out
end
EOF
looking-glass ispb 'show bgp ipv4 unicast neighbors 192.0.2.5 routes'
on edge vtysh << 'EOF'
configure terminal
ip prefix-list NOT-OURS seq 5 deny 198.51.100.0/24 le 32
ip prefix-list NOT-OURS seq 10 permit 0.0.0.0/0 le 32
route-map FROM-ISPA permit 10
 match ip address prefix-list NOT-OURS
exit
route-map FROM-ISPB permit 10
 match ip address prefix-list NOT-OURS
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 192.0.2.2 route-map FROM-ISPA in
  neighbor 192.0.2.6 route-map FROM-ISPB in
exit
exit
no route-map ALLOW permit 10
end
EOF
sleep 3
on edge ip route get 198.51.100.200
on web curl -sS -m 3 http://198.51.100.200/
on edge vtysh -c 'show bgp ipv4 unicast 203.0.113.0/24'
on edge ip route get 203.0.113.10
on edge vtysh << 'EOF'
configure terminal
route-map FROM-ISPA permit 10
 set local-preference 200
end
EOF
sleep 6
on edge vtysh -c 'show bgp ipv4 unicast 203.0.113.0/24'
on office traceroute -n -w 1 -q 1 -m 6 203.0.113.10
looking-glass cloud 'show bgp ipv4 unicast 198.51.100.0/24'
on edge vtysh -c 'write memory'
on edge cat /etc/frr/frr.conf
