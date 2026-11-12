# Wrong: everything works, but the rules were never written into
# /etc/nftables.conf, so the next boot loads the old firewall without NAT.
echo 'net.ipv4.ip_forward = 1' | on gw tee /etc/sysctl.d/90-gateway.conf > /dev/null
on gw sysctl -p /etc/sysctl.d/90-gateway.conf > /dev/null
on gw nft add table ip nat
on gw nft add chain ip nat postrouting '{ type nat hook postrouting priority srcnat; policy accept; }'
on gw nft add rule ip nat postrouting oifname "wan" masquerade
on gw nft add chain ip nat prerouting '{ type nat hook prerouting priority dstnat; policy accept; }'
on gw nft add rule ip nat prerouting iifname "wan" tcp dport 443 dnat to 10.1.0.20:8443
on gw nft add rule inet filter forward ct status dnat accept
