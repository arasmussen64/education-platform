# The reference fix, three faults in the origin's site file, then the edge's
# stale copies emptied:
#   - the pages said "public, max-age=86400", so the edge (and every browser)
#     kept the price list for a day. They become no-cache: kept, but asked
#     about before every use, cheaply with nginx's ETag. The copies the edge
#     kept before the fix stay good for their day, so the edge is purged;
#     browsers' copies can't be, and run out by themselves;
#   - the preflight's answer allowed the header X-Requested-With, and the
#     checkout's PUT sends Content-Type: application/json, which isn't a
#     simple request's: Content-Type joins the list;
#   - /board/ gave up on a connection idle for 30 seconds, sooner than the
#     board's 45-second ping, so every idle screen was cut. nginx's limit
#     goes to 300 seconds, above the ping; the edge's 120 is above it too.
# "on origin tee FILE <<'EOF'" writes the lines up to EOF into the file on
# origin, as root there; in the lab, nano does the same job by hand.
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
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin $cors_origin always;
            add_header Access-Control-Allow-Credentials "true" always;
            add_header Access-Control-Allow-Methods "GET, PUT, DELETE" always;
            add_header Access-Control-Allow-Headers "Content-Type, X-Requested-With" always;
            add_header Access-Control-Max-Age 600 always;
            add_header Vary Origin always;
            return 204;
        }
        proxy_pass http://127.0.0.1:8080;
        add_header Cache-Control "no-store" always;
        add_header Access-Control-Allow-Origin $cors_origin always;
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
sudo edge-purge
on office curl -s http://www.shop.test/news.html | grep version
