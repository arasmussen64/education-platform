# Wrong: the rule is in the output chain, which sees what leaves. The
# replies arrive through the input chain, where nothing accepts them.
mkdir -p ~/conntrack
sleep 6
sudo conntrack -L 2> /dev/null | grep ESTABLISHED | grep 'dport=8080 src' | awk '{print $7}' > /tmp/first-look
sleep 4
sudo conntrack -L 2> /dev/null | grep ESTABLISHED | grep 'dport=8080 src' | awk '{print $7}' > /tmp/second-look
sort /tmp/first-look /tmp/second-look | uniq -d | cut -d= -f2 > ~/conntrack/dashboard-port.txt
sudo tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
flush ruleset
table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state invalid drop
		tcp dport { 22, 8080 } accept
		udp dport 53 accept
	}
	chain forward {
		type filter hook forward priority filter; policy drop;
	}
	chain output {
		type filter hook output priority filter; policy accept;
		ct state established,related accept
	}
}
EOF
sudo nft -f /etc/nftables.conf
