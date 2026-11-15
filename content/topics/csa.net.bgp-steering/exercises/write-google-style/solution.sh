# The reference: read what the cloud says, then two route maps in depot's
# console, saved.
#   - Which circuit: the cloud's route arrives with metric 200 over ic1
#     (from 169.254.50.2) and metric 100 over ic2 (from 169.254.70.2). MED
#     is lower-is-better, so ic2 is the primary, and depot already chose it
#     for its own traffic: "best (MED)". Nothing on depot overrides that, so
#     the way out needs no change.
#   - The cloud's traffic: this cloud follows the MED depot sends, so TO-IC2
#     sends the depot's network with a MED of 100 and TO-IC1 with 200, the
#     Cloud Router's own two numbers. The higher MED is on the backup on
#     both sides, as Google's guide asks, so the two directions agree.
#   - Both route maps still let out only OURS, and each is made before it is
#     applied, so it takes effect at once (a route map changed while in use
#     takes about 5 seconds).
# "on depot vtysh << 'EOF'" sends the lines up to EOF to depot's console, as
# if they were typed at the depot# prompt; in the lab, typing them after
# "on depot vtysh" does the same.
on depot vtysh -c 'show bgp ipv4 unicast 10.60.0.0/16'
on depot vtysh << 'EOF'
configure terminal
route-map TO-IC1 permit 10
 match ip address prefix-list OURS
 set metric 200
exit
route-map TO-IC2 permit 10
 match ip address prefix-list OURS
 set metric 100
exit
router bgp 65002
 address-family ipv4 unicast
  neighbor 169.254.50.2 route-map TO-IC1 out
  neighbor 169.254.70.2 route-map TO-IC2 out
end
write memory
EOF
# Look, once the cloud's choice has moved: the cloud's view of the two MEDs,
# and its route, over ic2 alone.
for _ in $(seq 1 15); do looking-glass cloud 'show bgp ipv4 unicast 10.2.0.0/24' | grep 'best (MED)' > /dev/null && break; sleep 1; done
looking-glass cloud 'show bgp ipv4 unicast 10.2.0.0/24'
looking-glass cloud 'show ip route 10.2.0.0/24'
