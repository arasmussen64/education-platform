# Wrong: the versions and the default server fixed, and the resolver's line
# deleted instead of corrected. nginx staples again, from the address it
# looked up when it loaded its settings, but never looks the responder up
# again, and logs "no resolver defined" at every fetch.
on web sed -i 's/^\tssl_protocols TLSv1.3;/\tssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
on web sed -i 's/^    listen 443 ssl http2 default_server;$/    listen 443 ssl http2;/' /etc/nginx/sites-available/shop
on web sed -i '0,/^    listen 443 ssl http2;$/s//    listen 443 ssl http2 default_server;/' /etc/nginx/sites-available/shop
on web sed -i '/^    resolver 10.0.9.54;$/d' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner partner-sync || true
on monitor uptime-probe || true
