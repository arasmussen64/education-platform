# Wrong: two of the three faults fixed (web's firewall and the file
# server's pin); the printer's link is still set down in r2's file.
sudo sed -i 's/ip protocol icmp drop/icmp type echo-request drop/' /etc/netns/web/nftables.conf
on r2 sed -i '/10.0.2.30 lladdr/d' /etc/network/up
sudo netlab restart
