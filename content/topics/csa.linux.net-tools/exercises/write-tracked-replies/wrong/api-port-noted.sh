# Wrong: the right rule, but the port noted is the API's own, 8080, the
# port the dashboard's connection goes TO. The question was the port it
# comes from.
mkdir -p ~/conntrack
echo 8080 > ~/conntrack/dashboard-port.txt
sudo tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state invalid drop
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
