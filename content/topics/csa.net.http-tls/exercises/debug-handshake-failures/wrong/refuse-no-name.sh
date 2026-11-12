# Wrong: a default server that refuses every handshake, as for unknown names:
# the monitor, which sends no name, is now refused instead.
on web sed -i 's/^\tssl_protocols TLSv1.3;/\tssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
on web sed -i 's/^    resolver 10.0.9.54;$/    resolver 10.0.9.53;/' /etc/nginx/sites-available/shop
on web sed -i 's/^    listen 443 ssl http2 default_server;$/    listen 443 ssl http2;/' /etc/nginx/sites-available/shop
on web tee -a /etc/nginx/sites-available/shop > /dev/null << 'EOF'

server {
    listen 443 ssl http2 default_server;
    ssl_reject_handshake on;
}
EOF
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner partner-sync || true
on monitor uptime-probe || true
