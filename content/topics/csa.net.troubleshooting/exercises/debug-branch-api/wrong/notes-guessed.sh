# Every fix made, but the notes name the rate-limited hop as a fault and
# miss the provider's loss.
cat > ~/ticket/notes.txt <<'EOF'
fault-1 cause = icmp-rate-limited-hop
fault-1 evidence = mtr from client: 2.|-- 203.0.113.1 37.5%
fault-2 cause = duplicate-address
fault-2 evidence = arping from dc1: Received 6 response(s)
fault-3 cause = egress-filter-blocks-dependency
fault-3 evidence = upstream timed out (110: Connection timed out)
EOF
cat > ~/ticket/provider.txt <<'EOF'
last_clean_hop = 192.0.2.2
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
