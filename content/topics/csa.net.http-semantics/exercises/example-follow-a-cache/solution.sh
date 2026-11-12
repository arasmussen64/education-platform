netlab show
on office curl -sI http://www.shop.test/assets/app.3f9a.js
on office curl -sI http://www.shop.test/assets/app.3f9a.js
on office curl -sI http://www.shop.test/news.html
on office curl -s http://www.shop.test/news.html | grep version; sleep 5; on office curl -s http://www.shop.test/news.html | grep version
mkdir -p ~/example
etag=$(on office curl -sI http://origin.shop.test/index.html | tr -d '\r' | awk -F': ' 'tolower($1) == "etag" {print $2}'); echo "$etag"
on office curl -sI -H "If-None-Match: $etag" http://origin.shop.test/index.html | tr -d '\r' | head -n 1 | tee ~/example/conditional.txt
on office curl -s -H 'Cookie: session=alice' http://www.shop.test/account
on office curl -s -H 'Cookie: session=bob' http://www.shop.test/account
on office curl -sI -H 'Cookie: session=bob' http://www.shop.test/account | grep -i -e cache-control -e x-cache
on origin sed -i 's/Cache-Control "private"/Cache-Control "public, max-age=60"/' /etc/nginx/sites-available/shop
sudo systemctl reload nginx@origin; sleep 1
on office curl -s -H 'Cookie: session=alice' http://www.shop.test/account
on office curl -s -H 'Cookie: session=bob' http://www.shop.test/account
on origin sed -i 's/Cache-Control "public, max-age=60"/Cache-Control "private"/' /etc/nginx/sites-available/shop
sudo systemctl reload nginx@origin; sleep 1
on office curl -s -H 'Cookie: session=bob' http://www.shop.test/account
sudo edge-purge
on office curl -s -H 'Cookie: session=bob' http://www.shop.test/account
on office curl -si -X OPTIONS -H 'Origin: https://www.shop.test' -H 'Access-Control-Request-Method: PUT' -H 'Access-Control-Request-Headers: content-type' http://www.shop.test/api/basket > ~/example/preflight.txt
cat ~/example/preflight.txt
tr -d '\r' < ~/example/preflight.txt | awk -F': ' 'tolower($1) == "access-control-allow-origin" {print $2}' | tee ~/example/acao.txt
on office curl -si -X OPTIONS -H 'Origin: https://evil.test' -H 'Access-Control-Request-Method: PUT' -H 'Access-Control-Request-Headers: content-type' http://www.shop.test/api/basket
on office curl -si -X PUT -H 'Origin: https://www.shop.test' -H 'Cookie: session=alice' -H 'Content-Type: application/json' --data '{"items": 3}' http://www.shop.test/api/basket
on office curl -s -X PUT -H 'Cookie: session=alice' -H 'Content-Type: application/json' --data '{"items": 4}' http://www.shop.test/api/basket
on origin cat /etc/nginx/sites-available/shop
journalctl -u shop-app@origin -o cat | tail -n 4
on office curl -si --max-time 3 -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' http://www.shop.test/board/ | tr -d '\r' | tee ~/example/upgrade-answer.txt
head -n 1 ~/example/upgrade-answer.txt > ~/example/upgrade.txt
printf '%s' 'dGhlIHNhbXBsZSBub25jZQ==258EAFA5-E914-47DA-95CA-C5AB0DC85B11' | openssl sha1 -binary | base64
on origin cat /etc/order-board/board.conf; journalctl -u order-board@origin -o cat | grep -m 1 pinging
ls ~/example
