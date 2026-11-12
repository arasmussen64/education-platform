# Wrong: the API's own folder as certbot's webroot for api.shop.test, and
# plain HTTP for that name served from it, so that the CA finds its
# challenge files: every file in it, the orders included, then goes to
# anyone over plain HTTP, and nobody is asked for a certificate.
on web certbot certonly --server https://ca.shop.test:9000/acme/acme/directory \
  --webroot -w /var/www/html -d www.shop.test -m ops@shop.test --agree-tos --no-eff-email -n \
  --deploy-hook 'systemctl reload nginx@web'
on web tee /etc/nginx/sites-available/shop > /dev/null << 'EOF'
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

# Plain HTTP for the API's name: its folder, where certbot leaves the
# challenge files for it.
server {
    listen 80;
    server_name api.shop.test;
    root /srv/www/api;
}
EOF
on web rm /etc/nginx/sites-enabled/default
on web ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/shop
on web nginx -t
sudo systemctl reload nginx@web
sudo mkdir -p /srv/www/api/.well-known/acme-challenge
sudo chown -R root:root /srv/www/api/.well-known
on web certbot certonly --server https://ca.shop.test:9000/acme/acme/directory \
  --webroot -w /srv/www/api -d api.shop.test -m ops@shop.test --agree-tos --no-eff-email -n \
  --deploy-hook 'systemctl reload nginx@web'
on web tee -a /etc/nginx/sites-available/shop > /dev/null << 'EOF'

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
on web sed -i 's/^\tssl_protocols .*/\tssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
on web nginx -t
sudo systemctl reload nginx@web
sudo systemctl enable --now certbot@web.timer
sleep 1
on partner warehouse-sync
