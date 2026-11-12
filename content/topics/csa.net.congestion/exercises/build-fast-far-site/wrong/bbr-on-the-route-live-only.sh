# Wrong: shop sends the archive with BBR, but only because its route to the
# DR site was given BBR live (ip route ... congctl bbr), which the next boot
# builds again without it. fw lets HTTP/3 through, properly.
on shop ip route replace 10.0.6.0/24 via 10.0.5.1 dev eth1 congctl bbr
sudo sed -i 's/\(tcp dport { 22, 80, 443 } accept\)/\1\n        iifname "isp" oifname "shop" ip daddr 203.0.113.10 udp dport 443 accept/' /etc/netns/fw/nftables.conf
sudo systemctl reload nftables@fw
