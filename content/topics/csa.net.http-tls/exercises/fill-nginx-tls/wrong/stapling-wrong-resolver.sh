# Wrong: the resolver filled in as web itself, 127.0.0.1, where no name server
# listens: every fetch of the OCSP answer fails to look up the responder.
on web sed -i 's/^\tssl_protocols ___;/\tssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
on web tee /etc/nginx/sites-available/shop > /dev/null << 'EOF'
# The shop's sites on web: www.shop.test, the public shop, and
# api.shop.test, the partners' API, on one address, over HTTPS.
# Four values are missing here, each marked ___ (a fifth is in nginx.conf).

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
    listen 443 ssl;
    server_name www.shop.test;
    ssl_certificate     /etc/nginx/tls/www.shop.test/fullchain.pem;
    ssl_certificate_key /etc/nginx/tls/www.shop.test/privkey.pem;
    ssl_stapling on;
    resolver 127.0.0.1;
    root /srv/www/www;
}

server {
    listen 443 ssl;
    server_name api.shop.test;
    ssl_certificate     /etc/nginx/tls/api.shop.test/fullchain.pem;
    ssl_certificate_key /etc/nginx/tls/api.shop.test/privkey.pem;
    root /srv/www/api;
}
EOF
on web nginx -t
sudo systemctl reset-failed nginx@web
sudo systemctl restart nginx@web
sleep 1
on office curl -sI https://api.shop.test/ | head -n 1
