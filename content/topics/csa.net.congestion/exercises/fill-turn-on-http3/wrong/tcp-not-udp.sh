# Wrong: the firewall's gap is filled with TCP, which HTTPS already has, so
# QUIC's datagrams are still dropped. Caddy is filled in properly.
sudo sed -i 's/\.\.\. dport \.\.\. accept/tcp dport 443 accept/' /etc/netns/shop/nftables.conf
sudo systemctl restart nftables@shop
on shop sed -i 's/protocols h1 h2 \.\.\./protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl restart caddy@shop
