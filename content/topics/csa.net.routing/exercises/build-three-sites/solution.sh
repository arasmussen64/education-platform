# The reference: every router's static routes, typed into its console and
# saved with write memory. In the lab you can just as well type
# "on r1 vtysh" and then these lines at the r1# prompt.
#
# Each route to another site names its next hop and the interface it is
# on ("10.0.12.2 r2"), so it lives and dies with that cable. That matters
# on r1: its blackhole for 10.0.0.0/8 also holds the cables' own addresses,
# and a route that names only its next hop would, with its cable gone, have
# that next hop looked up again in r1's table, find it inside the blackhole
# and stay in use, at distance 1, sending the traffic into the blackhole
# while the backup waits.
#
# r1, the edge: a route to each other site over its direct cable, with a
# floating backup at distance 200 through the third router; the default
# route to the ISP's router; and a blackhole for the shop's whole
# 10.0.0.0/8, so that an internal address no site uses dies here instead
# of going to the ISP (the sites' own routes are longer, so they still win).
on r1 vtysh -c 'configure terminal' \
  -c 'ip route 10.2.0.0/24 10.0.12.2 r2' -c 'ip route 10.2.0.0/24 10.0.13.2 r3 200' \
  -c 'ip route 10.3.0.0/24 10.0.13.2 r3' -c 'ip route 10.3.0.0/24 10.0.12.2 r2 200' \
  -c 'ip route 0.0.0.0/0 198.51.100.1' \
  -c 'ip route 10.0.0.0/8 blackhole' \
  -c 'end' -c 'write memory'

# r2 and r3: the same for their two neighbours (each backup goes through
# the third router, and the way back has a backup too), and a default route
# to r1, the way to the internet.
on r2 vtysh -c 'configure terminal' \
  -c 'ip route 10.1.0.0/24 10.0.12.1 r1' -c 'ip route 10.1.0.0/24 10.0.23.2 r3 200' \
  -c 'ip route 10.3.0.0/24 10.0.23.2 r3' -c 'ip route 10.3.0.0/24 10.0.12.1 r1 200' \
  -c 'ip route 0.0.0.0/0 10.0.12.1' \
  -c 'end' -c 'write memory'
on r3 vtysh -c 'configure terminal' \
  -c 'ip route 10.1.0.0/24 10.0.13.1 r1' -c 'ip route 10.1.0.0/24 10.0.23.1 r2 200' \
  -c 'ip route 10.2.0.0/24 10.0.23.1 r2' -c 'ip route 10.2.0.0/24 10.0.13.1 r1 200' \
  -c 'ip route 0.0.0.0/0 10.0.13.1' \
  -c 'end' -c 'write memory'

# Look: every router's table, and the internet from the data centre.
for r in r1 r2 r3; do on "$r" vtysh -c 'show ip route static'; done
on dc curl -sS -m 3 http://203.0.113.10/
