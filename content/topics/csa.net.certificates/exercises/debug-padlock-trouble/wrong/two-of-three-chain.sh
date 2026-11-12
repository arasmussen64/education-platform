# Wrong: www.shop.test and the API's client CA fixed, and the API still
# sending its certificate without the intermediate.
on web sed -i -e 's#/etc/nginx/certs/www.pem#/etc/letsencrypt/live/www.shop.test/fullchain.pem#' -e 's#/etc/nginx/certs/www.key#/etc/letsencrypt/live/www.shop.test/privkey.pem#' /etc/nginx/sites-available/shop
on web certbot reconfigure --cert-name www.shop.test --deploy-hook 'systemctl reload nginx@web' -n
on web sed -i 's#ssl_client_certificate /etc/ssl/certs/ca-certificates.crt;#ssl_client_certificate /etc/nginx/partners-ca.pem;#' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner warehouse-sync
