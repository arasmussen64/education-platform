# Wrong: a new client certificate for the warehouse, made from the shop's
# own CA and put on partner in place of the warehouse's own from the Shop
# Partners CA: it isn't the shop's to replace, and the API still trusts the
# shop's root for clients.
on web sed -i -e 's#/etc/nginx/certs/www.pem#/etc/letsencrypt/live/www.shop.test/fullchain.pem#' -e 's#/etc/nginx/certs/www.key#/etc/letsencrypt/live/www.shop.test/privkey.pem#' /etc/nginx/sites-available/shop
on web certbot reconfigure --cert-name www.shop.test --deploy-hook 'systemctl reload nginx@web' -n
on web sed -i 's#/etc/nginx/tls/api.shop.test/cert.pem#/etc/nginx/tls/api.shop.test/fullchain.pem#' /etc/nginx/sites-available/shop
sudo /usr/local/lib/lab/sign-by-hand warehouse.partners.test 8760 /etc/netns/partner/warehouse/warehouse.pem /etc/netns/partner/warehouse/warehouse.key
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner warehouse-sync
