# Wrong: the three faults are fixed, and r1's forward chain accepts
# everything, so the internet can open connections to the laptops.
sudo sed -i 's#2001:db8:42::/56#2001:db8:42:a::/64#' /etc/netns/r1/radvd.conf
echo 'net.ipv6.conf.all.forwarding = 1' | on r1 tee -a /etc/sysctl.d/90-forward.conf > /dev/null
sudo sed -i '/meta l4proto ipv6-icmp drop/d; /hook forward/s/policy drop/policy accept/' /etc/netns/r1/nftables.conf
sudo netlab restart
