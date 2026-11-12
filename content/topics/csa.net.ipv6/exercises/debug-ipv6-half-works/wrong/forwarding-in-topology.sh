# Wrong: the advertisements and the firewall are fixed in r1's files, but
# IPv6 forwarding is switched on with a line added to the topology, which
# is the lab's scenery, instead of in r1's own settings. It works, and it
# lasts, but it changes the network the lab gave rather than r1.
sudo sed -i 's#2001:db8:42::/56#2001:db8:42:a::/64#' /etc/netns/r1/radvd.conf
sudo sed -i '/meta l4proto ipv6-icmp drop/d' /etc/netns/r1/nftables.conf
echo 'sysctl r1 net.ipv6.conf.all.forwarding=1' | sudo tee -a /etc/netlab/topology > /dev/null
sudo netlab restart
