# Wrong: all three faults are fixed and saved, but dc2's route map to the
# cloud was written afresh without its match line, so dc2 also sends the
# cloud its own 10.100.0.0/16 back, a route leak. The cloud drops its own
# network as a loop (its AS is in the path), so nothing changes on its side;
# dc2 still announces more than the data centre's summary.
on dc2 vtysh << 'EOF' > /dev/null
configure terminal
no route-map TO-CLOUD
route-map TO-CLOUD permit 10
 set as-path prepend 65001 65001
end
write memory
EOF
on dc1 vtysh << 'EOF' > /dev/null
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
# A route map changed while in use takes about 5 seconds to apply: wait
# until dc2 sends the leak, as it would by the time a learner runs the checks.
for _ in $(seq 1 20); do
  on dc2 vtysh -c 'show bgp ipv4 unicast neighbors 169.254.20.2 advertised-routes' | grep '10\.100\.0\.0/16' > /dev/null && break
  sleep 1
done
