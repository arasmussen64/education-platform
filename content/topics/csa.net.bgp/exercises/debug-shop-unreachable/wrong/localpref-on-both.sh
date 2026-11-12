# Wrong: the announcement and the leak are fixed, and both ISPs' routes
# now go through FROM-ISPA, so both get local preference 200: the tie
# goes to ISP B's shorter AS path, and traffic still leaves through B.
on edge vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 address-family ipv4 unicast
  no network 198.51.100.0/25
  network 198.51.100.0/24
exit
exit
route-map TO-ISPB permit 10
 match ip address prefix-list OURS
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 192.0.2.2 route-map FROM-ISPA in
exit
exit
end
write memory
EOF
# Long enough for a route map changed in use to reach the neighbours.
sleep 7
