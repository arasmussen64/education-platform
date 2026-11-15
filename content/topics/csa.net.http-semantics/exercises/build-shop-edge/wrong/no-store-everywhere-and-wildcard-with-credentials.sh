# Wrong, twice over, in two parts of the file that have nothing to do with
# each other (one file for both, because every contract run of this lab
# waits out the 75-second idle check: see content/README.md).
# 1. no-store on every kind of page: nothing is shared by mistake, and
#    nothing is kept either, so every customer fetches the assets again.
#    Fails assets-kept (and pages-asked-about).
# 2. The API allows every origin with "*" and credentials too. A browser
#    refuses a wildcard on a request that carries a cookie, so the shop's
#    own pages can't call it. Fails shop-sites-may-call.
on origin tee /etc/nginx/sites-available/shop > /dev/null << 'EOF'
# The shop's origin server, nginx on origin. The edge cache (www.shop.test)
# sits in front of it and keeps a copy of whatever these headers let a
# shared cache keep.

# Which browser origins may read the API's answers: the shop's two sites,
# each answered with its own name; anything else gets an empty value.
map $http_origin $cors_origin {
    default                 "";
    "https://shop.test"     $http_origin;
    "https://www.shop.test" $http_origin;
}

server {
    listen 80 default_server;
    server_name www.shop.test shop.test origin.shop.test;
    root /srv/www;
    index index.html;

    # Fingerprinted assets (app.3f9a.js): the next build gets new names.
    location /assets/ {
        add_header Cache-Control "no-store";
    }

    # The pages: the storefront and the price list.
    location ~ \.html$ {
        add_header Cache-Control "no-store";
    }

    # Each customer's own account page, from shop-app.
    location /account {
        proxy_pass http://127.0.0.1:8080;
        add_header Cache-Control "no-store";
    }

    # The basket API, from shop-app.
    location /api/ {
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin "*" always;
            add_header Access-Control-Allow-Credentials "true" always;
            add_header Access-Control-Allow-Methods "GET, PUT, DELETE" always;
            add_header Access-Control-Allow-Headers "Content-Type" always;
            add_header Access-Control-Max-Age 600 always;
            add_header Vary Origin always;
            return 204;
        }
        proxy_pass http://127.0.0.1:8080;
        add_header Cache-Control "no-store" always;
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Credentials "true" always;
        add_header Vary Origin always;
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
