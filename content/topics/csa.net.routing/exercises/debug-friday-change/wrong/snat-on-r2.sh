# Wrong: the internet and the card readers are fixed and saved, and r2
# rewrites the source of everything it sends to r3 into its own address
# (source NAT), so the stock app's replies have to come back through r2
# and the app answers. But the app now sees every office user as r2
# (10.0.23.1), r2's firewall isn't the one it had, and r3's route still
# points at the emergency link.
on r1 vtysh -c 'configure terminal' -c 'no ip route 0.0.0.0/0 198.51.100.254' -c 'ip route 0.0.0.0/0 198.51.100.1' \
  -c 'no ip route 10.2.128.0/17 blackhole' -c 'end' -c 'write memory' > /dev/null
on r2 nft add table ip nat
on r2 nft add chain ip nat postrouting '{ type nat hook postrouting priority srcnat; policy accept; }'
on r2 nft add rule ip nat postrouting oifname "r3" masquerade
