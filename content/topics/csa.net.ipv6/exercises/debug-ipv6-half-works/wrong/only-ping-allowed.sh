# Wrong: the advertisements and forwarding are fixed, and the firewall now
# lets ping through the forward chain (echo request and reply), but it
# still drops every other ICMPv6 message, "packet too big" among them, so
# big uploads still hang.
sudo sed -i 's#2001:db8:42::/56#2001:db8:42:a::/64#' /etc/netns/r1/radvd.conf
echo 'net.ipv6.conf.all.forwarding = 1' | on r1 tee -a /etc/sysctl.d/90-forward.conf > /dev/null
sudo sed -i 's#^\( *\)meta l4proto ipv6-icmp drop#\1icmpv6 type { echo-request, echo-reply } accept\n\1meta l4proto ipv6-icmp drop#' /etc/netns/r1/nftables.conf
sudo netlab restart
