# Wrong: only r1 has backups. When a cable fails, r1's traffic finds its
# way round, but the replies don't: r2 and r3 have no second route back,
# so the way back dies with the cable.
on r1 vtysh -c 'configure terminal' \
  -c 'ip route 10.2.0.0/24 10.0.12.2 r2' -c 'ip route 10.2.0.0/24 10.0.13.2 r3 200' \
  -c 'ip route 10.3.0.0/24 10.0.13.2 r3' -c 'ip route 10.3.0.0/24 10.0.12.2 r2 200' \
  -c 'ip route 0.0.0.0/0 198.51.100.1' -c 'ip route 10.0.0.0/8 blackhole' \
  -c 'end' -c 'write memory' > /dev/null
on r2 vtysh -c 'configure terminal' \
  -c 'ip route 10.1.0.0/24 10.0.12.1 r1' -c 'ip route 10.3.0.0/24 10.0.23.2 r3' \
  -c 'ip route 0.0.0.0/0 10.0.12.1' -c 'end' -c 'write memory' > /dev/null
on r3 vtysh -c 'configure terminal' \
  -c 'ip route 10.1.0.0/24 10.0.13.1 r1' -c 'ip route 10.2.0.0/24 10.0.23.1 r2' \
  -c 'ip route 0.0.0.0/0 10.0.13.1' -c 'end' -c 'write memory' > /dev/null
