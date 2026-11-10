# Wrong: without the connection-tracking rule, the replies to connections
# this machine makes are dropped on their way in, so it can't reach the
# office's monitoring endpoint (or anything else).
sudo tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
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
