# Wrong: the rules are loaded from a file in the home folder and the
# service isn't enabled, so the first reboot leaves the server with no
# firewall at all.
cat > ~/firewall.nft <<'EOF'
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
sudo nft -f ~/firewall.nft
