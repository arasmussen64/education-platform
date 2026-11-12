# Wrong: the firewall's gap lets in UDP 443 and 4433 as well, a port QUIC is
# often tried on, "for later". Nothing uses 4433, so it's one more way in.
# Caddy is filled in properly.
sudo sed -i 's/\.\.\. dport \.\.\. accept/udp dport { 443, 4433 } accept/' /etc/netns/shop/nftables.conf
sudo systemctl restart nftables@shop
on shop sed -i 's/protocols h1 h2 \.\.\./protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl restart caddy@shop
