# Wrong: the policy says drop, and the chain ends with a rule that accepts
# everything, "to be tightened later". The policy is never reached, so the
# office can reach every port: the database's and the unused one are
# answered (refused) instead of dropped. It reads as default-deny at a
# glance, the file parses, and the service is enabled.
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
		accept
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
