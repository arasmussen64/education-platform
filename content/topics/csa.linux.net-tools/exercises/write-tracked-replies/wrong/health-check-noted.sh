# Wrong: the right rule, but the port noted is from a line whose state is
# TIME_WAIT: one of the dashboard's health checks, already closed, not
# the connection it keeps open.
mkdir -p ~/conntrack
sleep 10
sudo conntrack -L 2> /dev/null | grep TIME_WAIT | grep 'dport=8080 src' | head -n 1 | awk '{print $7}' | cut -d= -f2 > ~/conntrack/dashboard-port.txt
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
