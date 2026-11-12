# Wrong: the walkthrough's classic mistake left in place: the masquerade
# rule names no interface, so traffic going into the shop's network is
# translated too, and the app sees every customer as gw (10.1.0.1).
# Everything else is done and saved.
echo 'net.ipv4.ip_forward = 1' | on gw tee /etc/sysctl.d/90-gateway.conf > /dev/null
on gw sysctl -p /etc/sysctl.d/90-gateway.conf > /dev/null
on gw nft add table ip nat
on gw nft add chain ip nat postrouting '{ type nat hook postrouting priority srcnat; policy accept; }'
on gw nft add rule ip nat postrouting masquerade
on gw nft add chain ip nat prerouting '{ type nat hook prerouting priority dstnat; policy accept; }'
on gw nft add rule ip nat prerouting iifname "wan" tcp dport 443 dnat to 10.1.0.20:8443
on gw nft add rule inet filter forward ct status dnat accept
on gw sh -c '{ echo "flush ruleset"; nft list ruleset; } > /etc/nftables.conf'
