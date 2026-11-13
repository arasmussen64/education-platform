# Names the first lossy hop twice, with no hop before the trouble.
cat > ~/ticket/notes.txt <<'EOF'
fault-1 cause = provider-packet-loss
fault-1 evidence = mtr from client: 4.|-- 198.51.100.2 10.0%, 0.0% at 192.0.2.2
fault-2 cause = duplicate-address
fault-2 evidence = arping from dc1: Received 6 response(s), two MACs
fault-3 cause = egress-filter-blocks-dependency
fault-3 evidence = upstream timed out (110: Connection timed out) while connecting to upstream
EOF
cat > ~/ticket/provider.txt <<'EOF'
last_clean_hop = 198.51.100.2
first_lossy_hop = 198.51.100.2
EOF
sudo systemctl disable --now old-lb.service
on lb arping -q -U -c 2 -I eth0 10.20.0.80
on api3 tee /etc/nftables.conf > /dev/null <<'EOF'
#!/usr/sbin/nft -f
# api3's firewall, as the new server image ships it.
flush ruleset

table inet filter {
	chain input {
		type filter hook input priority filter; policy drop;
		iif lo accept
		ct state established,related accept
		tcp dport { 22, 80 } accept
		icmp type echo-request accept
	}
	chain output {
		type filter hook output priority filter; policy drop;
		oif lo accept
		ct state established,related accept
		udp dport 53 accept
		tcp dport { 80, 443 } accept
		ip daddr 10.20.0.50 tcp dport 5000 accept
		counter
	}
}
EOF
sudo systemctl reload nftables@api3
