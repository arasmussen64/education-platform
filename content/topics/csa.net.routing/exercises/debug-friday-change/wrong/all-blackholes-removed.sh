# Wrong: the internet and the stock app are fixed and saved, and to make
# the card readers work every blackhole on r1 was deleted, the shop's
# 10.0.0.0/8 with the stale one, so internal addresses no site uses now
# follow the default route to the ISP, which sends them straight back.
on r3 vtysh -c 'configure terminal' -c 'no ip route 10.1.0.0/24 10.0.13.1' -c 'ip route 10.1.0.0/24 10.0.23.1' -c 'end' -c 'write memory' > /dev/null
on r1 vtysh -c 'configure terminal' -c 'no ip route 0.0.0.0/0 198.51.100.254' -c 'ip route 0.0.0.0/0 198.51.100.1' \
  -c 'no ip route 10.2.128.0/17 blackhole' -c 'no ip route 10.0.0.0/8 blackhole' -c 'end' -c 'write memory' > /dev/null
