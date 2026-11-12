# Wrong: everything but the timer: nothing renews the certificates, which run out tomorrow.
for name in www.shop.test api.shop.test; do
  on web certbot certonly --server https://ca.shop.test:9000/acme/acme/directory \
    --webroot -w /var/www/html -d "$name" -m ops@shop.test --agree-tos --no-eff-email -n \
    --deploy-hook 'systemctl reload nginx@web'
done
#   - port 80: ACME's challenge files for both names, from the webroot
#     certbot used, and every other request for www sent to HTTPS;
#   - www.shop.test on 443 and api.shop.test on 8443, each with certbot's
#     live/ full chain and key, so every renewal is the one nginx reads;
#   - the API asks for a client certificate, trusts only the Shop
#     Partners CA for it, and refuses a client without a valid one
#     (ssl_verify_client on); the public site asks for none;
#   - "http2" on the listen lines (nginx 1.24); the versions in
#     nginx.conf's SSL Settings, where in nginx 1.24 the default server of
#     each address and port decides them.
on web tee /etc/nginx/sites-available/shop > /dev/null << 'EOF'
# The shop's sites on web: www.shop.test, the public shop, on 443, and
# api.shop.test, the partners' API, on 8443, both with certificates from
# the shop CA's ACME service, which certbot renews.

# Plain HTTP: ACME's challenge files, and the shop sent to HTTPS.
server {
    listen 80;
    server_name www.shop.test;
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 80;
    server_name api.shop.test;
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    location / {
        return 404;
    }
}

server {
    listen 443 ssl http2;
    server_name www.shop.test;
    ssl_certificate     /etc/letsencrypt/live/www.shop.test/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.shop.test/privkey.pem;
    root /srv/www/www;
}

# Partners only: a client must show a certificate from the Shop Partners CA.
server {
    listen 8443 ssl http2;
    server_name api.shop.test;
    ssl_certificate     /etc/letsencrypt/live/api.shop.test/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.shop.test/privkey.pem;
    ssl_client_certificate /etc/nginx/partners-ca.pem;
    ssl_verify_client on;
    root /srv/www/api;
}
EOF
on web rm /etc/nginx/sites-enabled/default
on web ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/shop
on web sed -i 's/^\tssl_protocols .*/\tssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner warehouse-sync
