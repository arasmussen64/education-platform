# Wrong: r1's blackholes cover all of 10.0.0.0/8 except 10.0.0.0/14, the
# block that holds every site, as if a blackhole mustn't overlap the
# sites' own networks. It may (each site's route is longer, so it still
# wins), and leaving the /14 out lets an unused address in it, such as
# 10.2.200.1, follow r1's default route to the ISP, which sends it
# straight back: a loop.
on r1 vtysh -c 'configure terminal' \
  -c 'ip route 10.2.0.0/24 10.0.12.2 r2' -c 'ip route 10.2.0.0/24 10.0.13.2 r3 200' \
  -c 'ip route 10.3.0.0/24 10.0.13.2 r3' -c 'ip route 10.3.0.0/24 10.0.12.2 r2 200' \
  -c 'ip route 0.0.0.0/0 198.51.100.1' \
  -c 'ip route 10.4.0.0/14 blackhole' -c 'ip route 10.8.0.0/13 blackhole' -c 'ip route 10.16.0.0/12 blackhole' \
  -c 'ip route 10.32.0.0/11 blackhole' -c 'ip route 10.64.0.0/10 blackhole' -c 'ip route 10.128.0.0/9 blackhole' \
  -c 'end' -c 'write memory' > /dev/null
on r2 vtysh -c 'configure terminal' \
  -c 'ip route 10.1.0.0/24 10.0.12.1 r1' -c 'ip route 10.1.0.0/24 10.0.23.2 r3 200' \
  -c 'ip route 10.3.0.0/24 10.0.23.2 r3' -c 'ip route 10.3.0.0/24 10.0.12.1 r1 200' \
  -c 'ip route 0.0.0.0/0 10.0.12.1' -c 'end' -c 'write memory' > /dev/null
on r3 vtysh -c 'configure terminal' \
  -c 'ip route 10.1.0.0/24 10.0.13.1 r1' -c 'ip route 10.1.0.0/24 10.0.23.1 r2 200' \
  -c 'ip route 10.2.0.0/24 10.0.23.1 r2' -c 'ip route 10.2.0.0/24 10.0.13.1 r1 200' \
  -c 'ip route 0.0.0.0/0 10.0.13.1' -c 'end' -c 'write memory' > /dev/null
