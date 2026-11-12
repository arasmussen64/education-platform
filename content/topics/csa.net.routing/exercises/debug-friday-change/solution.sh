# The reference: the evidence for each fault, then its fix, saved.
#
# 1. The internet. r1's default route is installed, but its next hop,
#    198.51.100.254, isn't the ISP's router (198.51.100.1), and nothing
#    answers r1's ARP question for it: ip neigh shows it INCOMPLETE, then
#    FAILED. The fix is the next hop the design names.
on office curl -sS -m 3 http://203.0.113.10/
on r1 ip route show default
on r1 ip neigh show dev wan
on r1 vtysh -c 'configure terminal' -c 'no ip route 0.0.0.0/0 198.51.100.254' -c 'ip route 0.0.0.0/0 198.51.100.1' -c 'end' -c 'write memory'
on r1 ip route show default
on office curl -sS -m 3 http://203.0.113.10/

# 2. The stock app. Ping works and the app times out: r2's connection
#    table holds the office's SYN as [UNREPLIED], and its invalid-drop
#    counter climbs, because the app's replies never pass r2. A trace from
#    the office shows hop 3 as 10.0.13.2, r3's end of the emergency link:
#    r3 sends everything for the office that way. The fix is r3's route to
#    the office through r2, not a change to r2's firewall.
on office curl -sS -m 3 http://10.3.0.10:8080/
on r2 conntrack -L
on r2 nft list chain inet filter forward
on office traceroute -n -I -q 1 -w 1 -m 5 10.3.0.10
on r3 vtysh -c 'show ip route 10.1.0.0/24'
on r3 vtysh -c 'configure terminal' -c 'no ip route 10.1.0.0/24 10.0.13.1' -c 'ip route 10.1.0.0/24 10.0.23.1' -c 'end' -c 'write memory'
on office curl -sS -m 3 http://10.3.0.10:8080/

# 3. The card readers. With the internet back, the tills reach the payment
#    provider and the readers don't. r1's kernel refuses 10.2.200.10
#    (Invalid argument: a blackhole), because a blackhole for 10.2.128.0/17,
#    left from a migration, is a longer prefix than the store's /16. It
#    goes: r4 drops the store's own unused addresses now. The blackhole for
#    the shop's whole 10.0.0.0/8 stays, so unused internal addresses still
#    die at r1.
on reader curl -sS -m 3 http://203.0.113.10/
on r1 ip route get 10.2.200.10
on r1 vtysh -c 'show ip route 10.2.200.10'
on r1 vtysh -c 'configure terminal' -c 'no ip route 10.2.128.0/17 blackhole' -c 'end' -c 'write memory'
on reader curl -sS -m 3 http://203.0.113.10/
