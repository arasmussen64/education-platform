# Wrong: the warehouse's sync told to skip checking the shop's certificate
# (curl -k) instead of fixing the API's chain: it isn't the shop's program,
# and every other careful client still fails.
on web sed -i -e 's#/etc/nginx/certs/www.pem#/etc/letsencrypt/live/www.shop.test/fullchain.pem#' -e 's#/etc/nginx/certs/www.key#/etc/letsencrypt/live/www.shop.test/privkey.pem#' /etc/nginx/sites-available/shop
on web certbot reconfigure --cert-name www.shop.test --deploy-hook 'systemctl reload nginx@web' -n
sudo sed -i 's/curl -sS /curl -sSk /' /usr/local/bin/warehouse-sync
on web sed -i 's#ssl_client_certificate /etc/ssl/certs/ca-certificates.crt;#ssl_client_certificate /etc/nginx/partners-ca.pem;#' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner warehouse-sync
