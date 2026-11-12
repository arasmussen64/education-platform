# The reference: two route maps added in edge's console, then saved.
# "on edge vtysh << 'EOF'" sends the lines up to EOF to edge's console, as if
# they were typed at the edge# prompt; in the lab, typing them after
# "on edge vtysh" does the same.
#   - Your own traffic: FROM-DX1 accepts the cloud's prefix over dx1, as
#     FROM-CLOUD does, and gives it local preference 200, above the default
#     100, so edge sends its traffic over dx1 while that session is up.
#   - The cloud's traffic: the cloud honours prefix length and AS path, and
#     edge may announce only 10.1.0.0/24, so TO-DX2 makes the path over dx2
#     longer by prepending edge's own AS twice. Over dx1 the path is one
#     network long, over dx2 three, and the shorter one wins.
#   - The route maps are made before they are applied, so each takes effect
#     at once (a route map changed while in use takes about 5 seconds).
on edge vtysh << 'EOF'
configure terminal
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 200
exit
route-map TO-DX2 permit 10
 match ip address prefix-list OURS
 set as-path prepend 65001 65001
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.20.2 route-map TO-DX2 out
end
write memory
EOF
# Look, once the cloud's choice has moved: both sides' paths, and the
# cloud's view of the two AS paths.
for _ in $(seq 1 15); do looking-glass cloud 'show ip route 10.1.0.0/24' | grep 'via dx2' > /dev/null || break; sleep 1; done
on edge vtysh -c 'show bgp ipv4 unicast 10.100.0.0/16'
looking-glass cloud 'show bgp ipv4 unicast 10.1.0.0/24'
