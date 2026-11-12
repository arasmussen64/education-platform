# Wrong: shop sends the archive with BBR, but only because its route to the
# DR site was given BBR live (ip route ... congctl bbr), which the next boot
# builds again without it. The site's two faults are fixed properly.
on shop ip route replace 10.0.6.0/24 via 10.0.5.1 dev eth1 congctl bbr
on shop sed -i 's/protocols h1 h2$/protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl reload caddy@shop
sudo sed -i 's/udp dport 4433 accept/udp dport 443 accept/' /etc/netns/shop/nftables.conf
sudo systemctl reload nftables@shop
