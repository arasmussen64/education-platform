# Wrong: the internet and the card readers are fixed and saved, and the
# path was made symmetric the other way round: r1 now sends the data
# centre's traffic over the emergency link too. The stock app answers,
# and nothing between the office and the data centre is inspected.
on r1 vtysh -c 'configure terminal' -c 'no ip route 0.0.0.0/0 198.51.100.254' -c 'ip route 0.0.0.0/0 198.51.100.1' \
  -c 'no ip route 10.2.128.0/17 blackhole' \
  -c 'no ip route 10.3.0.0/24 10.0.12.2' -c 'ip route 10.3.0.0/24 10.0.13.2' -c 'end' -c 'write memory' > /dev/null
