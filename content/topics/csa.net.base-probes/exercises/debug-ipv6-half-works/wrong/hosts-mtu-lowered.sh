# Wrong: the advertisements and forwarding are fixed, and instead of
# letting "packet too big" through, the laptops' MTU is lowered to the
# narrow link's, in their own network files. Uploads work; the rules say
# no MTU changes, and r1 still drops what IPv6 needs.
sudo sed -i 's#2001:db8:42::/56#2001:db8:42:a::/64#' /etc/netns/r1/radvd.conf
echo 'net.ipv6.conf.all.forwarding = 1' | on r1 tee -a /etc/sysctl.d/90-forward.conf > /dev/null
echo 'ip link set eth0 mtu 1400' | on h1 tee -a /etc/network/up > /dev/null
echo 'ip link set eth0 mtu 1400' | on h2 tee -a /etc/network/up > /dev/null
sudo netlab restart
