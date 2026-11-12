# Wrong: the resolver line put in api's server block, not www's. www still
# staples, from the address nginx looked up when it loaded its settings, but
# stapling takes the resolver of the site's own server, so www has none and
# never looks the responder up again.
on web tee /etc/nginx/sites-available/shop > /dev/null << 'EOF'
# The shop's sites on web: www.shop.test, the public shop, and
# api.shop.test, the partners' API, on one address, over HTTPS.

# Plain HTTP for either name: the same page, on HTTPS.
server {
    listen 80;
    server_name www.shop.test api.shop.test;
    return 301 https://$host$request_uri;
}

# A name with no site here, or no name at all: no certificate.
server {
    listen 443 ssl http2 default_server;
    ssl_reject_handshake on;
}

server {
    listen 443 ssl http2;
    server_name www.shop.test;
    ssl_certificate     /etc/nginx/tls/www.shop.test/fullchain.pem;
    ssl_certificate_key /etc/nginx/tls/www.shop.test/privkey.pem;
    ssl_stapling on;
    root /srv/www/www;
}

server {
    listen 443 ssl http2;
    server_name api.shop.test;
    ssl_certificate     /etc/nginx/tls/api.shop.test/fullchain.pem;
    ssl_certificate_key /etc/nginx/tls/api.shop.test/privkey.pem;
    resolver 10.0.9.53;
    root /srv/www/api;
}
EOF
on web ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/shop
on web sed -i 's/^\tssl_protocols .*/\tssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
on web nginx -t
sudo systemctl enable --now nginx@web
sleep 1
on office curl -sI https://www.shop.test/ | head -n 3
