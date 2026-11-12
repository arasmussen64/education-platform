# Wrong: the right firewall is loaded live from a copy in /tmp, and shop's
# /etc/nftables.conf keeps its gaps, so the next boot leaves shop without a
# firewall. Caddy is filled in properly.
sed 's/\.\.\. dport \.\.\. accept/udp dport 443 accept/' /etc/netns/shop/nftables.conf > /tmp/firewall.conf
on shop nft -f /tmp/firewall.conf
on shop sed -i 's/protocols h1 h2 \.\.\./protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl restart caddy@shop
