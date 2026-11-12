# Wrong: the file server's pin is kept and given the address of its
# current network card, in r2's file and live. It works until the card
# changes (here, at the next boot, as when a card is replaced), because a
# pinned entry is never checked again. The other two faults are fixed in
# their files and applied live.
mac=$(on files cat /sys/class/net/eth0/address)
on r2 sed -i "s/lladdr [0-9a-f:]* dev lan/lladdr $mac dev lan/; /ip link set prn down/d" /etc/network/up
on r2 ip neigh replace 10.0.2.30 lladdr "$mac" dev lan nud permanent
on r2 ip link set prn up
sudo sed -i 's/ip protocol icmp drop/icmp type echo-request drop/' /etc/netns/web/nftables.conf
sudo systemctl reload nftables@web
