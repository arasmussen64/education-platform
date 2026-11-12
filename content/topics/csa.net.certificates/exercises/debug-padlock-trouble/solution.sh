# The reference: three faults, each fixed in web's files.
#   1. www.shop.test served a copy of an old certificate, made by hand in
#      /etc/nginx/certs/, which had expired: it now reads certbot's live/
#      names, and its renewal settings gain a hook that reloads nginx, so
#      every renewal reaches it.
#   2. api.shop.test sent cert.pem, its certificate without the
#      intermediate: a client that trusts only the root (the warehouse's
#      sync) couldn't build the chain. It sends fullchain.pem.
#   3. Once the chain was fixed, the API refused the warehouse: it trusted
#      the machine's trust store, the shop's root, for client certificates,
#      which the Shop Partners CA's certificate isn't in (and which every
#      server certificate the shop's CA issues would satisfy). It trusts the
#      Shop Partners CA alone.
# sed -i edits a file in place; # separates its parts, as the paths are
# full of /.
on web sed -i -e 's#/etc/nginx/certs/www.pem#/etc/letsencrypt/live/www.shop.test/fullchain.pem#' -e 's#/etc/nginx/certs/www.key#/etc/letsencrypt/live/www.shop.test/privkey.pem#' /etc/nginx/sites-available/shop
on web certbot reconfigure --cert-name www.shop.test --deploy-hook 'systemctl reload nginx@web' -n
on web sed -i 's#/etc/nginx/tls/api.shop.test/cert.pem#/etc/nginx/tls/api.shop.test/fullchain.pem#' /etc/nginx/sites-available/shop
on web sed -i 's#ssl_client_certificate /etc/ssl/certs/ca-certificates.crt;#ssl_client_certificate /etc/nginx/partners-ca.pem;#' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner warehouse-sync
