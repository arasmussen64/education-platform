# Wrong: the ten-port rule from the walkthrough's exhaustion step is never
# taken away, and is saved with the rest, so connections to srv's ports
# 9000 and 9001 still share ten ports.
echo 'net.ipv4.ip_forward = 1' | on gw tee /etc/sysctl.d/90-gateway.conf > /dev/null
on gw sysctl -p /etc/sysctl.d/90-gateway.conf > /dev/null
on gw nft add table ip nat
on gw nft add chain ip nat postrouting '{ type nat hook postrouting priority srcnat; policy accept; }'
on gw nft add rule ip nat postrouting oifname "wan" masquerade
on gw nft add chain ip nat prerouting '{ type nat hook prerouting priority dstnat; policy accept; }'
on gw nft add rule ip nat prerouting iifname "wan" tcp dport 443 dnat to 10.1.0.20:8443
on gw nft add rule inet filter forward ct status dnat accept
on gw nft insert rule ip nat postrouting oifname "wan" ip protocol tcp tcp dport { 9000, 9001 } snat to 198.51.100.2:20000-20009
on gw sh -c '{ echo "flush ruleset"; nft list ruleset; } > /etc/nftables.conf'
