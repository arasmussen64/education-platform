# Wrong: the firewall's gap lets in every UDP port, not just the one QUIC
# uses. Caddy is filled in properly.
sudo sed -i 's/\.\.\. dport \.\.\. accept/udp dport 1-65535 accept/' /etc/netns/shop/nftables.conf
sudo systemctl restart nftables@shop
on shop sed -i 's/protocols h1 h2 \.\.\./protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl restart caddy@shop
