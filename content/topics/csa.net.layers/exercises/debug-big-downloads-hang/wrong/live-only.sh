# Wrong: all three faults fixed with live commands only. Everything works
# until the next boot, which builds the machines from their files again.
sed 's/ip protocol icmp drop/icmp type echo-request drop/' /etc/netns/web/nftables.conf | on web nft -f -
on r2 ip neigh del 10.0.2.30 dev lan
on r2 ip link set prn up
on office ping -c 1 -W 2 10.0.3.5 > /dev/null || true
