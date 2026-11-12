# Wrong: the "conditional" request went to the edge, without the validator,
# so it was an ordinary request and the answer saved is a 200 with the whole
# page. The other two answers are saved right.
mkdir -p ~/example
on office curl -sI http://www.shop.test/index.html | tr -d '\r' | head -n 1 > ~/example/conditional.txt
on office curl -si -X OPTIONS -H 'Origin: https://www.shop.test' -H 'Access-Control-Request-Method: PUT' -H 'Access-Control-Request-Headers: content-type' http://www.shop.test/api/basket | tr -d '\r' | awk -F': ' 'tolower($1) == "access-control-allow-origin" {print $2}' > ~/example/acao.txt
on office curl -si --max-time 3 -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' http://www.shop.test/board/ | tr -d '\r' | head -n 1 > ~/example/upgrade.txt
