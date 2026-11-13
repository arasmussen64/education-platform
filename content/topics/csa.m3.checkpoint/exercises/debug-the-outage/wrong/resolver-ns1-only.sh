# Wrong: the resolver stops asking ns2, which still serves its old copy.
for _ in $(seq 1 30); do on r2 ip route show 10.30.0.0/24 | grep tun2 > /dev/null && break; sleep 1; done
sudo sed -i '/stub-addr: 10.30.0.200/d' /etc/netns/resolver/unbound/unbound.conf
sudo systemctl reset-failed unbound@resolver
sudo systemctl restart unbound@resolver
sleep 2
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
