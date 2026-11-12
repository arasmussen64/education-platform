# Wrong: both files are filled in properly and the firewall is loaded, but
# Caddy, which failed at boot, is never started again, so the site is down.
sudo sed -i 's/\.\.\. dport \.\.\. accept/udp dport 443 accept/' /etc/netns/shop/nftables.conf
sudo systemctl restart nftables@shop
on shop sed -i 's/protocols h1 h2 \.\.\./protocols h1 h2 h3/' /etc/caddy/Caddyfile
