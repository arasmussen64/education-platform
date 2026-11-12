sudo sed -i 's#2001:db8:42::/56#2001:db8:42::/64#' /etc/netlab/r1/radvd.conf
sudo sed -i 's#2001:db8:42:a::1/64#2001:db8:42::1/64#' /etc/netlab/r1/up
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/netlab/r1/sysctl.conf > /dev/null
sudo sed -i '/meta l4proto ipv6-icmp drop/d' /etc/netlab/r1/nftables.conf
sudo systemctl restart netlab; sleep 6
