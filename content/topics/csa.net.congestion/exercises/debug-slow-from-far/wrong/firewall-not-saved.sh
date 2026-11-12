# Wrong: the right firewall is loaded live from a copy in /tmp, and shop's
# /etc/nftables.conf still opens the wrong port, so the next boot loads the
# old rules again. BBR and Caddy are fixed properly.
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-bbr.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
on shop sed -i 's/protocols h1 h2$/protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl reload caddy@shop
sed 's/udp dport 4433 accept/udp dport 443 accept/' /etc/netns/shop/nftables.conf > /tmp/firewall.conf
on shop nft -f /tmp/firewall.conf
