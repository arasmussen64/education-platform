# The reference: each ___ filled in, here with sed -i, which edits a file in
# place (in the lab, nano does it by hand), then the script run, and nginx
# started (it starts at every boot by itself, once its files are right).
#   - the intermediate is a CA (CA:TRUE) that may have no CA under it
#     (pathlen:0), so it can sign the API's certificate and no other CA;
#   - the API's certificate names api.shop.test in its subjectAltName and
#     is for a server (serverAuth); the warehouse's is for a client
#     (clientAuth);
#   - the full chain is the API's own certificate first, then the
#     intermediate's: nginx takes the first certificate in the file as the
#     server's, to go with its key;
#   - the API sends the full chain, trusts the Shop Partners CA, and only
#     it, for client certificates, and refuses a client without a valid
#     one (on).
sed -i -e 's/basicConstraints=critical,___/basicConstraints=critical,CA:TRUE,pathlen:0/' \
  -e 's/subjectAltName=___/subjectAltName=DNS:api.shop.test/' \
  -e "s/'extendedKeyUsage=___' 'keyUsage=critical,digitalSignature' > api.ext/'extendedKeyUsage=serverAuth' 'keyUsage=critical,digitalSignature' > api.ext/" \
  -e 's/^cat ___ ___ > fullchain.pem$/cat api.pem intermediate.pem > fullchain.pem/' \
  -e "s/'extendedKeyUsage=___' 'keyUsage=critical,digitalSignature' > warehouse.ext/'extendedKeyUsage=clientAuth' 'keyUsage=critical,digitalSignature' > warehouse.ext/" \
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
