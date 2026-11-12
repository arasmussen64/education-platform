# Wrong: the local preferences are the wrong way round for the VPN: it
# gets the highest, so edge sends the office's traffic to the cloud over the
# internet while both circuits are up.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list OFFICE seq 5 permit 10.1.0.0/21
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
 set local-preference 400
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
  aggregate-address 10.1.0.0/21 summary-only
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.30.2 route-map TO-DX1 out
  neighbor 169.254.20.2 route-map FROM-DX2 in
  neighbor 169.254.20.2 route-map TO-DX2 out
  neighbor 169.254.10.2 route-map FROM-VPN in
  neighbor 169.254.10.2 route-map TO-VPN out
end
write memory
EOF
