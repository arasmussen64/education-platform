# The reference: the new session, configured in edge's console and saved.
# "on edge vtysh << 'EOF'" sends the lines up to EOF to edge's console, as
# if they were typed at the edge# prompt.
#   - CLOUD-WEB names the one prefix edge takes from the cloud; FROM-CLOUD
#     permits only that, so whatever else the cloud offers, now or later,
#     ends at the route map's implicit deny.
#   - TO-CLOUD sends only OURS, the shop's own prefix (edge's existing list),
#     so nothing edge learned from the ISPs goes on to the cloud.
#   - The route maps are made before they are applied, so each takes effect
#     at once.
#   - The direct path wins on its own: its AS path, 65100, is one network
#     long, shorter than either ISP's.
on edge vtysh << 'EOF'
configure terminal
ip prefix-list CLOUD-WEB seq 5 permit 203.0.113.0/24
route-map FROM-CLOUD permit 10
 match ip address prefix-list CLOUD-WEB
exit
route-map TO-CLOUD permit 10
 match ip address prefix-list OURS
exit
router bgp 65001
 neighbor 169.254.30.2 remote-as 65100
 neighbor 169.254.30.2 timers connect 5
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-CLOUD in
  neighbor 169.254.30.2 route-map TO-CLOUD out
end
write memory
EOF
# Look, once edge's kernel sends the cloud's traffic over the private link
# (the session takes a few seconds).
for _ in $(seq 1 30); do on edge ip route get 203.0.113.10 | grep 'via 169.254.30.2' > /dev/null && break; sleep 1; done
on edge vtysh -c 'show bgp summary'
on edge vtysh -c 'show bgp ipv4 unicast neighbors 169.254.30.2 routes'
looking-glass cloud 'show bgp ipv4 unicast neighbors 169.254.30.1 routes'
