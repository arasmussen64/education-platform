# Wrong: the stock app and the card readers are fixed and saved, and a
# default route to the ISP's router was added, but Friday's default route
# to 198.51.100.254 was left beside it. Both have distance 1, so r1
# installs both and shares the internet's traffic between them (ECMP),
# half of it towards a next hop nobody answers for. The office may well
# reach the internet when it's tried (the kernel passes over a next hop
# whose neighbour entry has FAILED, until that entry expires), which is
# why the check reads r1's default route itself.
on r3 vtysh -c 'configure terminal' -c 'no ip route 10.1.0.0/24 10.0.13.1' -c 'ip route 10.1.0.0/24 10.0.23.1' -c 'end' -c 'write memory' > /dev/null
on r1 vtysh -c 'configure terminal' -c 'ip route 0.0.0.0/0 198.51.100.1' \
  -c 'no ip route 10.2.128.0/17 blackhole' -c 'end' -c 'write memory' > /dev/null
