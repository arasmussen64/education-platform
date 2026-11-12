sudo sed -i 's#2001:db8:42::/56#2001:db8:42:a::/64#' /etc/netlab/r1/radvd.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/netlab/r1/sysctl.conf > /dev/null
sudo sed -i '/meta l4proto ipv6-icmp drop/d' /etc/netlab/r1/nftables.conf
printf 'table ip6 nat {\n    chain postrouting {\n        type nat hook postrouting priority srcnat; policy accept;\n        oifname "wan" masquerade\n    }\n}\n' | sudo tee -a /etc/netlab/r1/nftables.conf > /dev/null
sudo systemctl restart netlab; sleep 6
