# Wrong: the pin is kept, with the file server's new card's address, and
# applied live. Works until the card (here: the next boot) changes again.
mac=$(on files cat /sys/class/net/eth0/address)
sudo sed -i "s/lladdr [0-9a-f:]* dev lan/lladdr $mac dev lan/; /ip link set prn down/d" /etc/netlab/r2/up
sudo sed -i 's/ip protocol icmp drop/icmp type echo-request drop/' /etc/netlab/web/nftables.conf
on r2 ip neigh replace 10.0.2.30 lladdr $mac dev lan nud permanent
on r2 ip link set prn up; on r2 ip route add 10.0.3.0/24 dev prn 2>/dev/null || true
on web nft -f /etc/netlab/web/nftables.conf
