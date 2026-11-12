# Wrong: the allow-origin value was saved from the preflight sent as
# https://evil.test, which gets no Access-Control-Allow-Origin at all, so
# the file is empty. The other two answers are saved right.
mkdir -p ~/example
etag=$(on office curl -sI http://origin.shop.test/index.html | tr -d '\r' | awk -F': ' 'tolower($1) == "etag" {print $2}')
on office curl -sI -H "If-None-Match: $etag" http://origin.shop.test/index.html | tr -d '\r' | head -n 1 > ~/example/conditional.txt
on office curl -si -X OPTIONS -H 'Origin: https://evil.test' -H 'Access-Control-Request-Method: PUT' -H 'Access-Control-Request-Headers: content-type' http://www.shop.test/api/basket | tr -d '\r' | awk -F': ' 'tolower($1) == "access-control-allow-origin" {print $2}' > ~/example/acao.txt
on office curl -si --max-time 3 -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' http://www.shop.test/board/ | tr -d '\r' | head -n 1 > ~/example/upgrade.txt
