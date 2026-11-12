# Wrong: shop sends with BBR, but set live only, with sysctl -w, so the next
# boot puts CUBIC back. The site's two faults are fixed properly.
on shop sysctl -w net.ipv4.tcp_congestion_control=bbr
on shop sed -i 's/protocols h1 h2$/protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl reload caddy@shop
sudo sed -i 's/udp dport 4433 accept/udp dport 443 accept/' /etc/netns/shop/nftables.conf
sudo systemctl reload nftables@shop
