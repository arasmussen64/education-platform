# Wrong: certbot's fresh certificate copied by hand over the expired copy.
# It works today, and the next renewal goes the way the last one went.
on web cp -L /etc/letsencrypt/live/www.shop.test/fullchain.pem /etc/nginx/certs/www.pem
on web cp -L /etc/letsencrypt/live/www.shop.test/privkey.pem /etc/nginx/certs/www.key
on web sed -i 's#/etc/nginx/tls/api.shop.test/cert.pem#/etc/nginx/tls/api.shop.test/fullchain.pem#' /etc/nginx/sites-available/shop
on web sed -i 's#ssl_client_certificate /etc/ssl/certs/ca-certificates.crt;#ssl_client_certificate /etc/nginx/partners-ca.pem;#' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner warehouse-sync
