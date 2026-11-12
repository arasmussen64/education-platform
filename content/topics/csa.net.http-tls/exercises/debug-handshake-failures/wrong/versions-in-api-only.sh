# Wrong: TLS 1.2 allowed in api's own server block, nginx.conf left alone. With
# www's server the default for port 443, nginx 1.24 takes the versions
# from it, so api's line is ignored and the sync is still refused.
on web sed -i 's/^    listen 443 ssl http2 default_server;$/    listen 443 ssl http2;/' /etc/nginx/sites-available/shop
on web sed -i '0,/^    listen 443 ssl http2;$/s//    listen 443 ssl http2 default_server;/' /etc/nginx/sites-available/shop
on web sed -i 's/^    resolver 10.0.9.54;$/    resolver 10.0.9.53;/' /etc/nginx/sites-available/shop
on web sed -i 's/^    server_name api.shop.test;$/    server_name api.shop.test;\n    ssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner partner-sync || true
on monitor uptime-probe || true
