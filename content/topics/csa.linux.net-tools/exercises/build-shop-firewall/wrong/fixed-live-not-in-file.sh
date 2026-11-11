# Wrong: the file was written without the name server's port and loaded;
# when the office couldn't resolve names, the missing rule was added to the
# running firewall with nft add rule, and never to the file. Everything
# works today, the file parses and the service is enabled, and the next
# reboot loads a firewall that drops the office's name lookups.
sudo tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		tcp dport { 22, 8080 } accept
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
sudo nft add rule inet filter input udp dport 53 accept
