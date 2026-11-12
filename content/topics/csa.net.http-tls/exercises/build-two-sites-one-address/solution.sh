# The reference: the shop's two sites in one site file on web, the versions
# in nginx.conf, the site switched on, and nginx started now and at every
# boot. "on web tee FILE <<'EOF'" writes the lines up to EOF into the file
# on web, as root there; in the lab, nano does the same job by hand.
#   - port 80: one server for both names, redirecting to the same path on
#     HTTPS ($host is the name asked for, $request_uri the path and query);
#   - a default server for port 443 that refuses every handshake, so a
#     name with no site of its own (or no name) gets no certificate;
#     "http2" on one listen line switches HTTP/2 on for the whole port in
#     nginx 1.24, so every line may as well say it;
#   - one server per name, each with its own full chain and key, chosen by
#     SNI; stapling on www, with the resolver nginx asks for the
#     responder's address when it fetches an answer;
#   - versions in nginx.conf's SSL Settings: in nginx 1.24 the default
#     server of an address and port decides them for every site there.
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
    resolver 10.0.9.53;
    root /srv/www/www;
}

server {
    listen 443 ssl http2;
    server_name api.shop.test;
    ssl_certificate     /etc/nginx/tls/api.shop.test/fullchain.pem;
    ssl_certificate_key /etc/nginx/tls/api.shop.test/privkey.pem;
    root /srv/www/api;
}
EOF
on web ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/shop
on web sed -i 's/^\tssl_protocols .*/\tssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
on web nginx -t
sudo systemctl enable --now nginx@web
sleep 1
on office curl -sI https://www.shop.test/ | head -n 3
