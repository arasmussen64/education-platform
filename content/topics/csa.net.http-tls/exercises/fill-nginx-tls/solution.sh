# The reference: the five gaps filled, then nginx on web started again.
# sed -i changes the one line in nginx.conf (inside web's own /etc/nginx
# folder, so sed can replace the file), and "on web tee FILE <<'EOF'"
# writes the lines up to EOF into the site file, as root there; in the lab,
# nano does the same job by hand.
#   - nginx.conf: TLS 1.2 and 1.3, and nothing older;
#   - the default server's listen line: http2, which in nginx 1.24 switches
#     HTTP/2 on for every site on port 443;
#   - www: stapling on, and the shop's resolver, which nginx asks for the
#     responder's address each time it fetches an answer;
#   - the second site's name: api.shop.test.
# nginx couldn't start at boot with the gaps, and systemd stops retrying a
# service that fails five times in a few seconds; reset-failed lets it try
# again at once.
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
    resolver 10.0.9.53;
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
