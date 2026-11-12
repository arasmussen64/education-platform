sudo sed -i 's#2001:db8:42::/56#2001:db8:42:a::/64#' /etc/netlab/r1/radvd.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/netlab/r1/sysctl.conf > /dev/null
echo 'ip link set eth0 mtu 1400' | sudo tee -a /etc/netlab/h1/up /etc/netlab/h2/up > /dev/null
sudo systemctl restart netlab; sleep 6
