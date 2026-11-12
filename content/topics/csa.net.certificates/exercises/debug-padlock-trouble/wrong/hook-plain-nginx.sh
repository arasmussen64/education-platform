# Wrong: a deploy hook typed out of habit, systemctl reload nginx: on this
# lab machine the plain nginx unit only says where nginx really runs, so the
# hook reloads nothing.
on web sed -i -e 's#/etc/nginx/certs/www.pem#/etc/letsencrypt/live/www.shop.test/fullchain.pem#' -e 's#/etc/nginx/certs/www.key#/etc/letsencrypt/live/www.shop.test/privkey.pem#' /etc/nginx/sites-available/shop
on web certbot reconfigure --cert-name www.shop.test --deploy-hook 'systemctl reload nginx' -n
on web sed -i 's#/etc/nginx/tls/api.shop.test/cert.pem#/etc/nginx/tls/api.shop.test/fullchain.pem#' /etc/nginx/sites-available/shop
on web sed -i 's#ssl_client_certificate /etc/ssl/certs/ca-certificates.crt;#ssl_client_certificate /etc/nginx/partners-ca.pem;#' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner warehouse-sync
