# Wrong: the internet and the stock app are fixed and saved, and the card
# readers work because a route for their one /24 was added, longer than the
# stale blackhole. The blackhole is still there: every other address in the
# top half of the store's 10.2.0.0/16 still dies at r1.
on r3 vtysh -c 'configure terminal' -c 'no ip route 10.1.0.0/24 10.0.13.1' -c 'ip route 10.1.0.0/24 10.0.23.1' -c 'end' -c 'write memory' > /dev/null
on r1 vtysh -c 'configure terminal' -c 'no ip route 0.0.0.0/0 198.51.100.254' -c 'ip route 0.0.0.0/0 198.51.100.1' \
  -c 'ip route 10.2.200.0/24 10.0.14.2' -c 'end' -c 'write memory' > /dev/null
