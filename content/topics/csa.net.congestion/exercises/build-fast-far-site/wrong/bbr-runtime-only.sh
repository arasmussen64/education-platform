# Wrong: shop sends with BBR, but set live only, with sysctl -w, so the next
# boot puts CUBIC back. fw lets HTTP/3 through, properly.
on shop sysctl -w net.ipv4.tcp_congestion_control=bbr
sudo sed -i 's/\(tcp dport { 22, 80, 443 } accept\)/\1\n        iifname "isp" oifname "shop" ip daddr 203.0.113.10 udp dport 443 accept/' /etc/netns/fw/nftables.conf
sudo systemctl reload nftables@fw
