# Wrong: r2 and r3 are right and saved, but r1's routes were typed
# straight into its kernel with ip route add: they work until the next
# boot, which loses them, and FRR knows nothing of them (so r1 has no
# backups either).
on r1 ip route add 10.3.0.0/24 via 10.0.13.2
on r1 ip route add 10.2.0.0/24 via 10.0.12.2
on r2 vtysh -c 'configure terminal' -c 'ip route 10.1.0.0/24 10.0.12.1' -c 'ip route 10.1.0.0/24 10.0.23.2 200' -c 'ip route 10.3.0.0/24 10.0.23.2' -c 'ip route 10.3.0.0/24 10.0.12.1 200' -c 'end'
on r3 vtysh -c 'configure terminal' -c 'ip route 10.1.0.0/24 10.0.13.1' -c 'ip route 10.1.0.0/24 10.0.23.1 200' -c 'ip route 10.2.0.0/24 10.0.23.1' -c 'ip route 10.2.0.0/24 10.0.13.1 200' -c 'end'
for r in r1 r2 r3; do on "$r" vtysh -c 'write memory' > /dev/null; done
