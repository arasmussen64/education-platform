sudo sed -i 's#2001:db8:42::/56#2001:db8:42:a::/64#' /etc/netlab/r1/radvd.conf
sudo sed -i '/meta l4proto ipv6-icmp drop/d' /etc/netlab/r1/nftables.conf
sudo systemctl restart netlab; sleep 6
on r1 sysctl -qw net.ipv6.conf.all.forwarding=1
