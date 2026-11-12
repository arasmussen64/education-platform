# Wrong: the advertisement is made a /64, but the wrong one: the first /64
# of the office's block, 2001:db8:42::/64, with r1's LAN address moved to
# match, instead of the office's subnet 2001:db8:42:a::/64.
sudo sed -i 's#2001:db8:42::/56#2001:db8:42::/64#' /etc/netns/r1/radvd.conf
on r1 sed -i 's#2001:db8:42:a::1/64#2001:db8:42::1/64#' /etc/network/up
echo 'net.ipv6.conf.all.forwarding = 1' | on r1 tee -a /etc/sysctl.d/90-forward.conf > /dev/null
sudo sed -i '/meta l4proto ipv6-icmp drop/d' /etc/netns/r1/nftables.conf
sudo netlab restart
