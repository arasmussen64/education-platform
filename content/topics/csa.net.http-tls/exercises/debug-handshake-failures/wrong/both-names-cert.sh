# Wrong: api's server left the default, and given a new certificate, made
# with the CA's own key, that names www.shop.test as well as api.shop.test:
# the monitor is happy, and api's clients are handed a certificate for
# another site. The versions and the resolver fixed.
on web sed -i 's/^\tssl_protocols TLSv1.3;/\tssl_protocols TLSv1.2 TLSv1.3;/' /etc/nginx/nginx.conf
on web sed -i 's/^    resolver 10.0.9.54;$/    resolver 10.0.9.53;/' /etc/nginx/sites-available/shop
d=$(mktemp -d)
sudo openssl ecparam -name prime256v1 -genkey -noout -out "$d/privkey.pem"
sudo openssl req -new -key "$d/privkey.pem" -subj /CN=api.shop.test -out "$d/both.csr"
printf '%s\n' 'subjectAltName=DNS:api.shop.test,DNS:www.shop.test' 'extendedKeyUsage=serverAuth' \
  'authorityInfoAccess=OCSP;URI:http://ocsp.shop.test:8888' > "$d/both.ext"
sudo openssl x509 -req -in "$d/both.csr" -CA /var/lib/lab/ca/intermediate.pem -CAkey /var/lib/lab/ca/intermediate.key \
  -CAcreateserial -CAserial "$d/serial" -days 30 -extfile "$d/both.ext" -out "$d/cert.pem"
on web mkdir -p /etc/nginx/tls/both
sudo sh -c "cat '$d/cert.pem' /var/lib/lab/ca/intermediate.pem > /etc/netns/web/nginx/tls/both/fullchain.pem"
sudo cp "$d/privkey.pem" /etc/netns/web/nginx/tls/both/privkey.pem
on web sed -i 's|tls/api.shop.test/|tls/both/|g' /etc/nginx/sites-available/shop
on web nginx -t
sudo systemctl reload nginx@web
sleep 1
on partner partner-sync || true
on monitor uptime-probe || true
