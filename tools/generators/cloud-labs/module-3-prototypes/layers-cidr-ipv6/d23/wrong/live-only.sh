sed 's/ip protocol icmp drop/icmp type echo-request drop/' /etc/netlab/web/nftables.conf > /tmp/web.nft
on web nft -f /tmp/web.nft
on r2 ip neigh del 10.0.2.30 dev lan
on r2 ip link set prn up
on r2 ip route add 10.0.3.0/24 dev prn 2>/dev/null || true
