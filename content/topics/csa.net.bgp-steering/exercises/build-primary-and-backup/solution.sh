# The reference: edge configured in its console, then saved.
# "on edge vtysh << 'EOF'" sends the lines up to EOF to edge's console, as if
# they were typed at the edge# prompt; in the lab, typing them after
# "on edge vtysh" does the same.
#   - Two prefix lists: OFFICE, the one prefix edge announces, the summary
#     of the eight office networks (10.1.0.0/24 to 10.1.7.0/24 make one /21);
#     CLOUD, the one prefix edge takes from the cloud.
#   - Your own traffic: local preference 300 on what comes over dx1, 200 over
#     dx2, and the default 100 over the VPN, so dx1 wins, then dx2, then the
#     VPN.
#   - The cloud's traffic: AWS's documented communities, 7224:7300 (high) on
#     what goes out over dx1 and 7224:7100 (low) over dx2, which the cloud
#     turns into its own local preference, compared before anything else
#     but the prefix length. The cloud already ranks the VPN below both
#     circuits.
#   - The eight networks go into BGP with network lines and leave as one
#     summary: aggregate-address ... summary-only announces 10.1.0.0/21 and
#     holds back the eight /24s, which would be more than the cloud's limit
#     of 5 prefixes on a session.
#   - BFD on both circuits' sessions, so a silent failure is noticed in under
#     a second (300 ms x 3, FRR's defaults).
#   - The route maps are made before they are applied, so each takes effect
#     at once (a route map changed while in use takes about 5 seconds).
on edge vtysh << 'EOF'
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
# Look, once the cloud's traffic for the office takes dx1: what the cloud
# accepted over each session, its choice, and the BFD sessions.
for _ in $(seq 1 15); do looking-glass cloud 'show ip route 10.1.0.10' | grep 'via dx1' > /dev/null && break; sleep 1; done
looking-glass cloud 'show bgp summary'
looking-glass cloud 'show bgp ipv4 unicast 10.1.0.0/21'
on edge vtysh -c 'show bfd peers brief'
