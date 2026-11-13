# Mends the address and writes the ticket, and leaves api3's firewall.
cat > ~/ticket/notes.txt <<'EOF'
fault-1 cause = provider-packet-loss
fault-1 evidence = mtr from client: 4.|-- 198.51.100.2 10.0%, 0.0% at 192.0.2.2
fault-2 cause = duplicate-address
fault-2 evidence = arping from dc1: Received 6 response(s), two MACs
fault-3 cause = egress-filter-blocks-dependency
fault-3 evidence = upstream timed out (110: Connection timed out) while connecting to upstream
EOF
cat > ~/ticket/provider.txt <<'EOF'
last_clean_hop = 192.0.2.2
first_lossy_hop = 198.51.100.2
EOF
sudo systemctl disable --now old-lb.service
on lb arping -q -U -c 2 -I eth0 10.20.0.80
