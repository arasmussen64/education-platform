on edge vtysh -c 'show bgp ipv4 unicast 10.100.0.0/16'
on edge ip route show 10.100.0.0/16
looking-glass cloud 'show bgp ipv4 unicast 10.1.0.0/24'
on edge vtysh << 'EOF'
configure terminal
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 300
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-DX1 in
end
EOF
sleep 2
on edge vtysh -c 'show bgp ipv4 unicast 10.100.0.0/16'
on edge ip route show 10.100.0.0/16
on edge vtysh << 'EOF'
configure terminal
route-map TO-DX1 permit 10
 match ip address prefix-list OURS
 set metric 50
exit
route-map TO-DX2 permit 10
 match ip address prefix-list OURS
 set metric 100
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map TO-DX1 out
  neighbor 169.254.20.2 route-map TO-DX2 out
end
EOF
sleep 2
looking-glass cloud 'show bgp ipv4 unicast 10.1.0.0/24'
on edge vtysh << 'EOF'
configure terminal
route-map TO-DX1 permit 10
 no set metric
exit
route-map TO-DX2 permit 10
 no set metric
 set as-path prepend 65001 65001
end
EOF
sleep 7
looking-glass cloud 'show bgp ipv4 unicast 10.1.0.0/24'
looking-glass cloud 'show running-config' | grep -A 2 '^route-map FROM-DX1'
on edge vtysh << 'EOF'
configure terminal
route-map TO-DX1 permit 10
 set community 7224:7300
exit
route-map TO-DX2 permit 10
 no set as-path prepend
 set community 7224:7100
end
EOF
sleep 7
looking-glass cloud 'show bgp ipv4 unicast 10.1.0.0/24'
looking-glass cloud 'show ip route 10.1.0.0/24'
on office ping -i 0.2 -c 25 -q 10.100.0.10 &
sleep 2; sudo netlab link edge dx1 down; wait
on edge ip route show 10.100.0.0/16
sudo netlab link edge dx1 up
for _ in $(seq 1 30); do on edge ip route show 10.100.0.0/16 | grep 'dev dx1' > /dev/null && break; sleep 1; done
on office ping -i 0.2 -c 75 -q 10.100.0.10 &
sleep 2; sudo netlab link edge dx1 silent; wait
on edge vtysh -c 'show bgp neighbors 169.254.30.2' | grep -i 'last reset'
sudo netlab link edge dx1 restore
for _ in $(seq 1 30); do on edge ip route show 10.100.0.0/16 | grep 'dev dx1' > /dev/null && break; sleep 1; done
looking-glass cloud 'show bfd peers brief'
on edge vtysh << 'EOF'
configure terminal
router bgp 65001
 neighbor 169.254.30.2 bfd
 neighbor 169.254.20.2 bfd
end
EOF
sleep 3
on edge vtysh -c 'show bfd peers'
on office ping -i 0.2 -c 25 -q 10.100.0.10 &
sleep 2; sudo netlab link edge dx1 silent; wait
sudo netlab link edge dx1 restore
for _ in $(seq 1 30); do on edge ip route show 10.100.0.0/16 | grep 'dev dx1' > /dev/null && break; sleep 1; done
on edge vtysh -c 'write memory'
on edge cat /etc/frr/frr.conf
