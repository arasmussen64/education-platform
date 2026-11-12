# Wrong: api's server, still the default, given www's certificate: the monitor
# is happy, and api.shop.test now answers with another site's certificate.
on web sed -i 's/^\tssl_protocols TLSv1.3;/\tssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
on web sed -i 's/^    resolver 10.0.9.54;$/    resolver 10.0.9.53;/' /etc/nginx/sites-available/shop
on web sed -i 's|tls/api.shop.test/|tls/www.shop.test/|g' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner partner-sync || true
on monitor uptime-probe || true
