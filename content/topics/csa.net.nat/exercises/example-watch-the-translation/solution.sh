on office curl -sS -m 3 http://203.0.113.10/
on gw sysctl net.ipv4.ip_forward
echo 'net.ipv4.ip_forward = 1' | on gw tee /etc/sysctl.d/90-gateway.conf
on gw sysctl -p /etc/sysctl.d/90-gateway.conf
on gw timeout 6 tcpdump -nn -i wan tcp port 80 &
on office curl -sS -m 3 http://203.0.113.10/
wait
on gw nft add table ip nat
on gw nft add chain ip nat postrouting '{ type nat hook postrouting priority srcnat; policy accept; }'
on gw nft add rule ip nat postrouting oifname "wan" masquerade
on office curl -sS -m 3 http://203.0.113.10/
on gw conntrack -L -p tcp --dport 80
on gw nft add chain ip nat prerouting '{ type nat hook prerouting priority dstnat; policy accept; }'
on gw nft add rule ip nat prerouting iifname "wan" tcp dport 443 dnat to 10.1.0.20:8443
on client curl -sS -m 3 http://198.51.100.2:443/
on gw nft add rule inet filter forward ct status dnat accept
on client curl -sS -m 3 http://198.51.100.2:443/
on gw nft flush chain ip nat postrouting
on gw nft add rule ip nat postrouting masquerade
on client curl -sS -m 3 http://198.51.100.2:443/
on app tail -n 2 /var/log/nginx/access.log
on gw nft flush chain ip nat postrouting
on gw nft add rule ip nat postrouting oifname "wan" masquerade
on gw nft insert rule ip nat postrouting oifname "wan" ip protocol tcp tcp dport { 9000, 9001 } snat to 198.51.100.2:20000-20009
on office holdconns 15 203.0.113.10 9000
on gw conntrack -S
on office holdconns 5 203.0.113.10 9001
on gw conntrack -L -p tcp --dst 203.0.113.10
on gw nft flush chain ip nat postrouting
on gw nft add rule ip nat postrouting oifname "wan" masquerade
on gw sh -c '{ echo "flush ruleset"; nft list ruleset; } > /etc/nftables.conf'
on gw nft list ruleset
