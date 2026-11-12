# Wrong: the warehouse's certificate made for a server's use (serverAuth):
# nginx refuses it as a client's.
sed -i -e 's/basicConstraints=critical,___/basicConstraints=critical,CA:TRUE,pathlen:0/' \
  -e 's/subjectAltName=___/subjectAltName=DNS:api.shop.test/' \
  -e "s/'extendedKeyUsage=___' 'keyUsage=critical,digitalSignature' > api.ext/'extendedKeyUsage=serverAuth' 'keyUsage=critical,digitalSignature' > api.ext/" \
  -e 's/^cat ___ ___ > fullchain.pem$/cat api.pem intermediate.pem > fullchain.pem/' \
  -e "s/'extendedKeyUsage=___' 'keyUsage=critical,digitalSignature' > warehouse.ext/'extendedKeyUsage=serverAuth' 'keyUsage=critical,digitalSignature' > warehouse.ext/" \
  ~/bin/make-shop-certs
~/bin/make-shop-certs
on web sed -i -e 's#ssl_certificate     /etc/nginx/tls/___;#ssl_certificate     /etc/nginx/tls/fullchain.pem;#' \
  -e 's#ssl_client_certificate /etc/nginx/tls/___;#ssl_client_certificate /etc/nginx/tls/partners-ca.pem;#' \
  -e 's#ssl_verify_client ___;#ssl_verify_client on;#' /etc/nginx/sites-available/partner-api
on web nginx -t
sudo systemctl reset-failed nginx@web
sudo systemctl restart nginx@web
sleep 1
on partner curl -s --cacert /etc/warehouse/shop-root.pem --cert /etc/warehouse/warehouse.pem --key /etc/warehouse/warehouse.key https://api.shop.test:8443/ || echo "the warehouse can't reach the API"
