# Wrong: every route out to the data centre is there and saved, but r3 has
# no route back to the office, so the office's requests arrive and the
# replies are dropped at r3.
on r1 vtysh -c 'configure terminal' -c 'ip route 10.3.0.0/24 10.0.13.2' -c 'ip route 10.3.0.0/24 10.0.12.2 200' -c 'ip route 10.2.0.0/24 10.0.12.2' -c 'ip route 10.2.0.0/24 10.0.13.2 200' -c 'end'
on r2 vtysh -c 'configure terminal' -c 'ip route 10.1.0.0/24 10.0.12.1' -c 'ip route 10.1.0.0/24 10.0.23.2 200' -c 'ip route 10.3.0.0/24 10.0.23.2' -c 'ip route 10.3.0.0/24 10.0.12.1 200' -c 'end'
on r3 vtysh -c 'configure terminal' -c 'ip route 10.2.0.0/24 10.0.23.1' -c 'ip route 10.2.0.0/24 10.0.13.1 200' -c 'end'
for r in r1 r2 r3; do on "$r" vtysh -c 'write memory' > /dev/null; done
