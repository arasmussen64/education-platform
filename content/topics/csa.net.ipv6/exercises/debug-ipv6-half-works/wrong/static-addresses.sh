# Wrong: instead of fixing r1's advertisements, the laptops are given
# addresses by hand, in their own network files.
echo 'ip addr add 2001:db8:42:a::11/64 dev eth0' | on h1 tee -a /etc/network/up > /dev/null
echo 'ip addr add 2001:db8:42:a::12/64 dev eth0' | on h2 tee -a /etc/network/up > /dev/null
echo 'net.ipv6.conf.all.forwarding = 1' | on r1 tee -a /etc/sysctl.d/90-forward.conf > /dev/null
sudo sed -i '/meta l4proto ipv6-icmp drop/d' /etc/netns/r1/nftables.conf
sudo netlab restart
