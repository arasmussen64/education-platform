# Wrong: BBR is set properly, but instead of letting HTTP/3 through fw, it is
# switched off in Caddy, so browsers stop trying it: the site works, over
# HTTP/2 only.
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-bbr.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
on shop sed -i 's/^\tskip_install_trust$/\tskip_install_trust\n\tservers {\n\t\tprotocols h1 h2\n\t}/' /etc/caddy/Caddyfile
sudo systemctl reload caddy@shop
