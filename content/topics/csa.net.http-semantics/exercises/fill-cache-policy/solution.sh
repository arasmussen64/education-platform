# The reference: the origin's site file with its six gaps filled, then
# nginx on origin reloaded so that it reads the file. "on origin tee FILE
# <<'EOF'" writes the lines up to EOF into the file on origin, as root there;
# in the lab, nano does the same job by hand.
#   - assets: any cache, a year, and no revalidation on reload (immutable);
#   - pages: no-cache, "store it, but ask before every reuse", which with
#     nginx's ETag makes a browser's asking a cheap 304;
#   - the account page: private, the browser's cache only;
#   - the API: no-store, no cache at all;
#   - the board: the browser's own Upgrade value, and Connection "upgrade".
on origin tee /etc/nginx/sites-available/shop > /dev/null << 'EOF'
# The shop's origin server, nginx on origin. The edge cache (www.shop.test)
# sits in front of it and keeps a copy of whatever these headers let a
# shared cache keep. Six values are missing, each marked ___.

server {
    listen 80 default_server;
    server_name www.shop.test shop.test origin.shop.test;
    root /srv/www;
    index index.html;

    # Fingerprinted assets (app.3f9a.js): the next build gets new names.
    location /assets/ {
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # The pages: the storefront and the price list.
    location ~ \.html$ {
        add_header Cache-Control "no-cache";
    }

    # Each customer's own account page, from shop-app.
    location /account {
        proxy_pass http://127.0.0.1:8080;
        add_header Cache-Control "private";
    }

    # The basket API, from shop-app.
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        add_header Cache-Control "no-store" always;
    }

    # The staff order board, a WebSocket, from order-board.
    location /board/ {
        proxy_pass http://127.0.0.1:8090;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
    }
}
EOF
on origin nginx -t
sudo systemctl reload nginx@origin
sleep 1
on office curl -sI http://www.shop.test/assets/app.3f9a.js
