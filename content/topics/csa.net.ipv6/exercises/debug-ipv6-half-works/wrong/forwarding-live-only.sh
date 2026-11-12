# Wrong: the advertisements and the firewall are fixed in r1's files, and
# IPv6 forwarding is turned on live only, with sysctl -w, which the next
# boot forgets.
sudo sed -i 's#2001:db8:42::/56#2001:db8:42:a::/64#' /etc/netns/r1/radvd.conf
sudo sed -i '/meta l4proto ipv6-icmp drop/d' /etc/netns/r1/nftables.conf
sudo netlab restart
on r1 sysctl -qw net.ipv6.conf.all.forwarding=1
