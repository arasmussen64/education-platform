# The reference: one fix on dc2 and two on dc1, each typed in the router's
# console and saved. "on dc1 vtysh << 'EOF'" sends the lines up to EOF to
# dc1's console, as if they were typed at the dc1# prompt.
#   - dc2 tagged its routes to the cloud with AWS's low-preference community,
#     7224:7100, which this cloud, like Microsoft's, ignores, so the cloud
#     saw two equal paths and shared its traffic over both circuits. A
#     prepend makes the path over circuit 2 longer, which it does honour.
#   - dc1 passed the cloud's routes to core with the cloud's own address on
#     circuit 1, 169.254.30.2, as their next hop, which core can't reach
#     (`inaccessible` in core's BGP table), so the data centre used dc2's
#     routes. next-hop-self puts dc1's own address there, as dc2 does.
#   - dc1's BFD profile asked for a packet every 3000 ms, so with 3 missed a
#     silent failure took 9 seconds to notice, no faster than BGP's hold
#     time. 300 ms (FRR's default) x 3 notices it in under a second.
on dc2 vtysh << 'EOF'
configure terminal
route-map TO-CLOUD permit 10
 no set community
 set as-path prepend 65001 65001
end
write memory
EOF
on dc1 vtysh << 'EOF'
configure terminal
bfd
 profile CIRCUIT
  receive-interval 300
  transmit-interval 300
 exit
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 10.0.2.1 next-hop-self
end
write memory
EOF
# Look, once the cloud has moved its traffic to circuit 1 (a route map
# changed while in use takes about 5 seconds): its choice, core's, and
# dc1's BFD session.
for _ in $(seq 1 20); do looking-glass cloud 'show ip route 10.1.0.10' | grep 'via dx2' > /dev/null || break; sleep 1; done
looking-glass cloud 'show bgp ipv4 unicast 10.1.0.0/22'
on core vtysh -c 'show bgp ipv4 unicast 10.100.0.0/16'
on dc1 vtysh -c 'show bfd peers'
