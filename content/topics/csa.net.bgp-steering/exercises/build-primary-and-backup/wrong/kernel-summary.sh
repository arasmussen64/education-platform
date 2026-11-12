# Wrong: everything works and FRR's configuration is saved, but the summary
# is announced with a network line held up by a blackhole route typed into
# edge's kernel with ip route add. The next boot loses that route, the
# network line then finds nothing in the table, and edge announces nothing.
on edge ip route add blackhole 10.1.0.0/21
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
  network 10.1.0.0/21
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.30.2 route-map TO-DX1 out
  neighbor 169.254.20.2 route-map FROM-DX2 in
  neighbor 169.254.20.2 route-map TO-DX2 out
  neighbor 169.254.10.2 route-map FROM-VPN in
  neighbor 169.254.10.2 route-map TO-VPN out
end
write memory
EOF
