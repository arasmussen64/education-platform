# Wrong: everything else is right, but the eight office networks go out one
# by one, eight /24s on each session: more than the 5 prefixes the cloud
# accepts on a session, so it tears every session down and tries again a
# minute later, when the same thing happens.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list OFFICE seq 5 permit 10.1.0.0/21 le 24
ip prefix-list CLOUD seq 5 permit 10.100.0.0/16
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 300
exit
route-map FROM-DX2 permit 10
 match ip address prefix-list CLOUD
 set local-preference 200
exit
route-map FROM-VPN permit 10
 match ip address prefix-list CLOUD
exit
route-map TO-DX1 permit 10
 match ip address prefix-list OFFICE
 set community 7224:7300
exit
route-map TO-DX2 permit 10
 match ip address prefix-list OFFICE
 set community 7224:7100
exit
route-map TO-VPN permit 10
 match ip address prefix-list OFFICE
exit
router bgp 65001
 neighbor 169.254.30.2 bfd
 neighbor 169.254.20.2 bfd
 address-family ipv4 unicast
  network 10.1.0.0/24
  network 10.1.1.0/24
  network 10.1.2.0/24
  network 10.1.3.0/24
  network 10.1.4.0/24
  network 10.1.5.0/24
  network 10.1.6.0/24
  network 10.1.7.0/24
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.30.2 route-map TO-DX1 out
  neighbor 169.254.20.2 route-map FROM-DX2 in
  neighbor 169.254.20.2 route-map TO-DX2 out
  neighbor 169.254.10.2 route-map FROM-VPN in
  neighbor 169.254.10.2 route-map TO-VPN out
end
write memory
EOF
