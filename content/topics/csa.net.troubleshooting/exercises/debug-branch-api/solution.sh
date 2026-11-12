# A reference fix for "The branch's API calls". The notes come first, as
# the method asks: each cause and its evidence, written before anything is
# changed. (cat > FILE <<'EOF' writes the lines that follow, up to EOF, into
# FILE; on M tee FILE <<'EOF' does the same with a file on machine M.)
cat > ~/ticket/notes.txt <<'EOF'
# The incident notes.
fault-1 cause = provider-packet-loss
fault-1 evidence = mtr from client: 4.|-- 198.51.100.2 10.0% and 10% to the end, 0.0% at 192.0.2.2 (the 37.5% at 203.0.113.1 doesn't carry on: rate limiting); from dc1, loss starts at its first hop
fault-2 cause = duplicate-address
fault-2 evidence = on dc1 arping -b -c 3 -I eth1 10.20.0.80: Received 6 response(s), from lb's MAC and from lbold's
fault-3 cause = egress-filter-blocks-dependency
fault-3 evidence = api3 error.log: upstream timed out (110: Connection timed out) while connecting to upstream, upstream: "http://10.20.0.50:5000/stock"; HAProxy: apis/api3 ... 504; api3's output chain: counter packets rising
EOF

# Fault 1 is the provider's: loss starts on their last link, between isp2
# (192.0.2.2, the last clean hop) and dc1 (198.51.100.2, where it shows).
cat > ~/ticket/provider.txt <<'EOF'
last_clean_hop = 192.0.2.2
first_lossy_hop = 198.51.100.2
EOF

# Fault 2: lbold, the old load balancer, still runs its failover software,
# which takes the API's address and announces it every 20 seconds. Stop it
# and keep it from starting at boot; stopped, it lets go of the address.
sudo systemctl disable --now old-lb.service
# Then lb announces its address again at once, rather than in up to 30
# seconds, so the data centre's router stops sending to lbold.
on lb arping -q -U -c 2 -I eth0 10.20.0.80

# Fault 3: api3's firewall lets it open no connection to the data service
# on db (10.20.0.50, port 5000). Allow exactly that, in the file, and load it.
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
