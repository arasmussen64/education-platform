# Wrong: the default server and the resolver fixed; the versions left at TLS 1.3
# only, so the warehouse's TLS 1.2 client is still refused.
on web sed -i 's/^    listen 443 ssl http2 default_server;$/    listen 443 ssl http2;/' /etc/nginx/sites-available/shop
on web sed -i '0,/^    listen 443 ssl http2;$/s//    listen 443 ssl http2 default_server;/' /etc/nginx/sites-available/shop
on web sed -i 's/^    resolver 10.0.9.54;$/    resolver 10.0.9.53;/' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner partner-sync || true
on monitor uptime-probe || true
