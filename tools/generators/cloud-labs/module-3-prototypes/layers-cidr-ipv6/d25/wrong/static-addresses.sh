echo 'ip addr add 2001:db8:42:a::11/64 dev eth0' | sudo tee -a /etc/netlab/h1/up > /dev/null
echo 'ip addr add 2001:db8:42:a::12/64 dev eth0' | sudo tee -a /etc/netlab/h2/up > /dev/null
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/netlab/r1/sysctl.conf > /dev/null
sudo sed -i '/meta l4proto ipv6-icmp drop/d' /etc/netlab/r1/nftables.conf
sudo systemctl restart netlab; sleep 6
