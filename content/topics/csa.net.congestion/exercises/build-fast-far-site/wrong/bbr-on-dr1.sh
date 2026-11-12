# Wrong: BBR is set for good on dr1, the receiver, and shop, the sender,
# still uses CUBIC. Congestion control runs where the data is sent from, so
# the archive is as slow as before. fw lets HTTP/3 through, properly.
echo 'net.ipv4.tcp_congestion_control = bbr' | on dr1 tee /etc/sysctl.d/60-bbr.conf > /dev/null
on dr1 sysctl -p /etc/sysctl.d/60-bbr.conf
sudo sed -i 's/\(tcp dport { 22, 80, 443 } accept\)/\1\n        iifname "isp" oifname "shop" ip daddr 203.0.113.10 udp dport 443 accept/' /etc/netns/fw/nftables.conf
sudo systemctl reload nftables@fw
