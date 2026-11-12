# Wrong: the stock app and the card readers are fixed in FRR and saved,
# but the default route was fixed by typing it straight into r1's kernel:
# it works until the next boot, when FRR puts Friday's default back.
on r3 vtysh -c 'configure terminal' -c 'no ip route 10.1.0.0/24 10.0.13.1' -c 'ip route 10.1.0.0/24 10.0.23.1' -c 'end' -c 'write memory' > /dev/null
on r1 vtysh -c 'configure terminal' -c 'no ip route 10.2.128.0/17 blackhole' -c 'end' -c 'write memory' > /dev/null
on r1 ip route replace default via 198.51.100.1
