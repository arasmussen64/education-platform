# Wrong: Caddy's gap is filled with h2c (HTTP/2 without encryption), not
# HTTP/3, so Caddy never listens for QUIC. The firewall is filled in
# properly.
sudo sed -i 's/\.\.\. dport \.\.\. accept/udp dport 443 accept/' /etc/netns/shop/nftables.conf
sudo systemctl restart nftables@shop
on shop sed -i 's/protocols h1 h2 \.\.\./protocols h1 h2 h2c/' /etc/caddy/Caddyfile
sudo systemctl restart caddy@shop
