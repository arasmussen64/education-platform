# Wrong: two of the three. shop sends with BBR and Caddy offers HTTP/3, but
# the firewall still drops UDP 443, so browsers stay on HTTP/2.
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-bbr.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
on shop sed -i 's/protocols h1 h2$/protocols h1 h2 h3/' /etc/caddy/Caddyfile
sudo systemctl reload caddy@shop
