# Wrong: the Caddyfile is fixed, but Caddy is never reloaded, so the running
# site still leaves HTTP/3 out. BBR and the firewall are fixed properly.
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-bbr.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
on shop sed -i 's/protocols h1 h2$/protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo sed -i 's/udp dport 4433 accept/udp dport 443 accept/' /etc/netns/shop/nftables.conf
sudo systemctl reload nftables@shop
