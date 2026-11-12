# Wrong: the mistake made on purpose was never put back. The account pages
# still say "public, max-age=60", so the edge hands one customer's page to
# the next for a minute at a time. The three answers are saved right.
mkdir -p ~/example
etag=$(on office curl -sI http://origin.shop.test/index.html | tr -d '\r' | awk -F': ' 'tolower($1) == "etag" {print $2}')
on office curl -sI -H "If-None-Match: $etag" http://origin.shop.test/index.html | tr -d '\r' | head -n 1 > ~/example/conditional.txt
on origin sed -i 's/Cache-Control "private"/Cache-Control "public, max-age=60"/' /etc/nginx/sites-available/shop
sudo systemctl reload nginx@origin
on office curl -si -X OPTIONS -H 'Origin: https://www.shop.test' -H 'Access-Control-Request-Method: PUT' -H 'Access-Control-Request-Headers: content-type' http://www.shop.test/api/basket | tr -d '\r' | awk -F': ' 'tolower($1) == "access-control-allow-origin" {print $2}' > ~/example/acao.txt
on office curl -si --max-time 3 -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' http://www.shop.test/board/ | tr -d '\r' | head -n 1 > ~/example/upgrade.txt
