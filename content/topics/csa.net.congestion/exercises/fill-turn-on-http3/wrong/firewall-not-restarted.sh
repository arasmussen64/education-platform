# Wrong: both files are filled in properly and Caddy is started, but the
# firewall's unit is never started again, so shop still runs with no
# firewall at all: HTTP/3 works, and so does everything else.
sudo sed -i 's/\.\.\. dport \.\.\. accept/udp dport 443 accept/' /etc/netns/shop/nftables.conf
on shop sed -i 's/protocols h1 h2 \.\.\./protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl restart caddy@shop
