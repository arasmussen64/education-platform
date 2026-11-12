# Wrong: UDP 443 is added to the firewall, but the wrong port, 4433, is
# left open beside it. BBR and Caddy are fixed properly.
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-bbr.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
on shop sed -i 's/protocols h1 h2$/protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl reload caddy@shop
sudo sed -i 's/udp dport 4433 accept/udp dport { 443, 4433 } accept/' /etc/netns/shop/nftables.conf
sudo systemctl reload nftables@shop
