# Wrong: the database port is rejected, which answers the office at once
# with a reset and tells it the port exists; the spec said drop silently.
sudo tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		tcp dport { 22, 8080 } accept
		udp dport 53 accept
		tcp dport 5432 reject with tcp reset
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
