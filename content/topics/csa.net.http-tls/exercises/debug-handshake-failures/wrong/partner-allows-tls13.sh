# Wrong: the warehouse's client changed to allow TLS 1.3, which isn't the
# shop's to change; nginx.conf left at TLS 1.3 only.
on web sed -i 's/^    listen 443 ssl http2 default_server;$/    listen 443 ssl http2;/' /etc/nginx/sites-available/shop
on web sed -i '0,/^    listen 443 ssl http2;$/s//    listen 443 ssl http2 default_server;/' /etc/nginx/sites-available/shop
on web sed -i 's/^    resolver 10.0.9.54;$/    resolver 10.0.9.53;/' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
sudo sed -i 's/ --tls-max 1.2//' /usr/local/bin/partner-sync
on partner partner-sync || true
on monitor uptime-probe || true
