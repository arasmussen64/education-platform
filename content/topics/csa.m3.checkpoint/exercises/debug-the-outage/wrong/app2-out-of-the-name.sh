# Wrong: the serial is raised, but app2 is taken out of www.shop.test, so the shop runs on one web server.
for _ in $(seq 1 30); do on r2 ip route show 10.30.0.0/24 | grep tun2 > /dev/null && break; sleep 1; done
on ns1 sed -i -e 's/2026101501 ; serial/2026111201 ; serial/' -e '/^www .*10\.30\.0\.11/d' /etc/bind/db.shop.test
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
on r2 tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# r2's firewall for the traffic it forwards.
flush ruleset
table inet filter {
	chain forward {
		type filter hook forward priority filter; policy accept;
		# Nothing in the cloud may reach the office's administration ports.
		iifname { "tun1", "tun2" } oifname "eth0" tcp dport { 22, 3389 } counter drop
	}
}
EOF
sudo systemctl reload nftables@r2
on resolver unbound-control flush_zone shop.test > /dev/null
on resolver unbound-control flush_infra all > /dev/null
sleep 2
