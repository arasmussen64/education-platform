# Wrong: the firewall lets in every UDP port, not just the site's 443.
# BBR and Caddy are fixed properly.
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-bbr.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
on shop sed -i 's/protocols h1 h2$/protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl reload caddy@shop
sudo sed -i 's/udp dport 4433 accept/meta l4proto udp accept/' /etc/netns/shop/nftables.conf
sudo systemctl reload nftables@shop
