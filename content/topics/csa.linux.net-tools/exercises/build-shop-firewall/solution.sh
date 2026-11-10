# The reference firewall, written in one go; in the lab you'd use nano.
sudo tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# The shop server's firewall: nothing in but SSH, the API and the name
# server; replies to our own connections; and the machine talking to itself.
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		tcp dport { 22, 8080 } accept
		udp dport 53 accept
	}
	chain forward {
		type filter hook forward priority filter; policy drop;
	}
	chain output {
		type filter hook output priority filter; policy accept;
	}
}
EOF
sudo nft -f /etc/nftables.conf
sudo systemctl enable nftables
from-office nc -zv shop.internal 8080; from-office nc -zv -w 3 shop.internal 5432 || echo "5432 from the office: no answer at all, dropped"; nc -zv 127.0.0.1 5432; nc -zv monitor.office.internal 9100
sudo nft list ruleset
