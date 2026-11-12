# Wrong: fw lets every UDP port through to shop, not just the site's 443.
# BBR is set properly.
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-bbr.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
sudo sed -i 's/\(tcp dport { 22, 80, 443 } accept\)/\1\n        iifname "isp" oifname "shop" meta l4proto udp accept/' /etc/netns/fw/nftables.conf
sudo systemctl reload nftables@fw
