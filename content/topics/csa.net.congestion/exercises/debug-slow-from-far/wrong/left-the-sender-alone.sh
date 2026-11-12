# Wrong: two of the three. The site's faults are fixed; shop, the sender,
# still uses CUBIC (BBR stays on dr1, which only receives).
on shop sed -i 's/protocols h1 h2$/protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl reload caddy@shop
sudo sed -i 's/udp dport 4433 accept/udp dport 443 accept/' /etc/netns/shop/nftables.conf
sudo systemctl reload nftables@shop
