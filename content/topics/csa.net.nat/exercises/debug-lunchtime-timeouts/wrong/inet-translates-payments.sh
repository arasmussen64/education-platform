# Wrong: the customers' and the office's faults fixed, the payments moved
# to 198.51.100.2's whole port range, and the provider's router, inet,
# changed by hand to turn them into 198.51.100.3 on their way to srv. Every
# payment opens, but through a change on somebody else's machine, in no
# file of its own, which the next boot of inet takes away.
sudo sed -i -e 's/snat to 198.51.100.3:40000-40049/snat to 198.51.100.2/' \
  -e '/# Anything else./d' -e '/iifname "wan" masquerade/d' \
  -e 's#ip saddr 10.1.1.0/24#ip saddr 10.1.0.0/24#' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
on inet nft add table ip nat
on inet nft add chain ip nat postrouting '{ type nat hook postrouting priority srcnat; policy accept; }'
on inet nft add rule ip nat postrouting ip saddr 198.51.100.2 ip daddr 203.0.113.10 tcp dport 443 snat to 198.51.100.3
