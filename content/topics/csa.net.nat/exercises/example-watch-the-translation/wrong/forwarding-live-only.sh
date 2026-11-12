# Wrong: the rules are right and saved, but forwarding was turned on live
# only, with sysctl -w, so after the next boot gw forwards nothing.
on gw sysctl -qw net.ipv4.ip_forward=1
on gw nft add table ip nat
on gw nft add chain ip nat postrouting '{ type nat hook postrouting priority srcnat; policy accept; }'
on gw nft add rule ip nat postrouting oifname "wan" masquerade
on gw nft add chain ip nat prerouting '{ type nat hook prerouting priority dstnat; policy accept; }'
on gw nft add rule ip nat prerouting iifname "wan" tcp dport 443 dnat to 10.1.0.20:8443
on gw nft add rule inet filter forward ct status dnat accept
on gw sh -c '{ echo "flush ruleset"; nft list ruleset; } > /etc/nftables.conf'
