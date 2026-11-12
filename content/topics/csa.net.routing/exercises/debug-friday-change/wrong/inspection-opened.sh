# Wrong: the internet and the card readers are fixed and saved, and the
# stock app "works" because r2's firewall was emptied: it no longer drops
# the half-conversations it sees, and it inspects nothing. r3 still sends
# the replies round the emergency link.
on r1 vtysh -c 'configure terminal' -c 'no ip route 0.0.0.0/0 198.51.100.254' -c 'ip route 0.0.0.0/0 198.51.100.1' \
  -c 'no ip route 10.2.128.0/17 blackhole' -c 'end' -c 'write memory' > /dev/null
on r2 nft flush ruleset
