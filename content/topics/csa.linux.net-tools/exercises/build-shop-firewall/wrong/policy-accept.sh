# Wrong: the policy is accept with one drop rule, so every other port is
# wide open (and an unused port is refused, not dropped).
sudo tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy accept;
		iif lo accept
		ct state established,related accept
		tcp dport 5432 drop
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
