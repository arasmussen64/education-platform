# Wrong: every route is right on paper, but r1's routes to the other sites
# name only their next hop. When r1's cable to r2 goes, FRR looks 10.0.12.2
# up again in r1's table and finds it inside r1's own blackhole for
# 10.0.0.0/8 ("10.0.12.2 (recursive)"), so the dead route stays in use at
# distance 1 and the store's traffic goes into the blackhole while the
# backup waits.
on r1 vtysh -c 'configure terminal' \
  -c 'ip route 10.2.0.0/24 10.0.12.2' -c 'ip route 10.2.0.0/24 10.0.13.2 200' \
  -c 'ip route 10.3.0.0/24 10.0.13.2' -c 'ip route 10.3.0.0/24 10.0.12.2 200' \
  -c 'ip route 0.0.0.0/0 198.51.100.1' -c 'ip route 10.0.0.0/8 blackhole' \
  -c 'end' -c 'write memory' > /dev/null
on r2 vtysh -c 'configure terminal' \
  -c 'ip route 10.1.0.0/24 10.0.12.1' -c 'ip route 10.1.0.0/24 10.0.23.2 200' \
  -c 'ip route 10.3.0.0/24 10.0.23.2' -c 'ip route 10.3.0.0/24 10.0.12.1 200' \
  -c 'ip route 0.0.0.0/0 10.0.12.1' -c 'end' -c 'write memory' > /dev/null
on r3 vtysh -c 'configure terminal' \
  -c 'ip route 10.1.0.0/24 10.0.13.1' -c 'ip route 10.1.0.0/24 10.0.23.1 200' \
  -c 'ip route 10.2.0.0/24 10.0.23.1' -c 'ip route 10.2.0.0/24 10.0.13.1 200' \
  -c 'ip route 0.0.0.0/0 10.0.13.1' -c 'end' -c 'write memory' > /dev/null
