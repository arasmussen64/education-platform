# The reference: edge configured from nothing in its console, then saved.
# "on edge vtysh << 'EOF'" sends the lines up to EOF to edge's console, as
# if they were typed at the edge# prompt; in the lab, typing them after
# "on edge vtysh" does the same.
#   - Two prefix lists: OURS, the one prefix edge announces; NOT-OURS, which
#     refuses the shop's prefix and everything inside it (le 32) and lets
#     every other prefix through.
#   - Three route maps: TO-ISPS sends only OURS; FROM-ISPA takes everything
#     NOT-OURS lets through and gives it local preference 200, above the
#     default 100, so ISP A's paths win while that session is up; FROM-ISPB
#     filters the same way and leaves the preference alone, so ISP B's paths
#     are there to take over.
#   - The route maps are made before they are applied, so each takes effect
#     at once (a route map changed while in use takes about 5 seconds).
on edge vtysh << 'EOF'
configure terminal
ip prefix-list OURS seq 5 permit 198.51.100.0/24
ip prefix-list NOT-OURS seq 5 deny 198.51.100.0/24 le 32
ip prefix-list NOT-OURS seq 10 permit 0.0.0.0/0 le 32
route-map TO-ISPS permit 10
 match ip address prefix-list OURS
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
# Look, once edge's kernel sends the cloud's traffic to ISP A (the sessions
# take a few seconds): the sessions, the choice for the cloud's network,
# and the path.
for _ in $(seq 1 30); do on edge ip route get 203.0.113.10 | grep 'via 192.0.2.2' > /dev/null && break; sleep 1; done
on edge vtysh -c 'show bgp summary'
on edge vtysh -c 'show bgp ipv4 unicast 203.0.113.0/24'
on office traceroute -n -w 1 -q 1 -m 6 203.0.113.10
