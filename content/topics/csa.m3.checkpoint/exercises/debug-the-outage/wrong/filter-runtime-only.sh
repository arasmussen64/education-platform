# Wrong: the rule is deleted from r2's running firewall, not from its file, so the next boot brings it back.
for _ in $(seq 1 30); do on r2 ip route show 10.30.0.0/24 | grep tun2 > /dev/null && break; sleep 1; done
on ns1 sed -i 's/2026101501 ; serial/2026111201 ; serial/' /etc/bind/db.shop.test
sudo systemctl reload named@ns1
for _ in $(seq 1 30); do [ "$(on pc dig +short +time=1 +tries=1 @10.30.0.200 shop.test SOA | cut -d' ' -f3)" = 2026111201 ] && break; sleep 1; done
on app2 tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# app2's own firewall: SSH, and the web server for the shop's networks.
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		ct state invalid drop
		icmp type echo-request accept
		tcp dport 22 accept
		ip saddr { 10.10.0.0/24, 10.20.0.0/24 } tcp dport 80 accept
		counter
	}
}
EOF
sudo systemctl reload nftables@app2
h=$(on r2 nft -a list chain inet filter forward | awk '/oifname "tun2"/ {print $NF}')
on r2 nft delete rule inet filter forward handle "$h"
on resolver unbound-control flush_zone shop.test > /dev/null
on resolver unbound-control flush_infra all > /dev/null
sleep 2
