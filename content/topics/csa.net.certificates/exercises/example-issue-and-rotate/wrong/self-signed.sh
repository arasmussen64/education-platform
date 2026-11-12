# Wrong: a certificate made on web with "openssl req -x509", signed by its
# own key, served in place of one from the CA; certbot is used only for the
# serial numbers. No one trusts a certificate that signs itself.
mkdir -p ~/example
on web openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -days 30 -subj /CN=www.shop.test -addext subjectAltName=DNS:www.shop.test -keyout /etc/nginx/tls/www.shop.test/privkey.pem -out /etc/nginx/tls/www.shop.test/fullchain.pem
on web nginx -t && sudo systemctl reload nginx@web && sleep 1
on web certbot certonly --server https://ca.shop.test:9000/acme/acme/directory --webroot -w /var/www/html -d www.shop.test -m ops@shop.test --agree-tos --no-eff-email -n
on web certbot reconfigure --cert-name www.shop.test --deploy-hook 'systemctl reload nginx@web' -n
on web openssl x509 -in /etc/letsencrypt/live/www.shop.test/cert.pem -noout -serial | tee ~/example/first.txt
on web certbot renew --cert-name www.shop.test --force-renewal --no-random-sleep-on-renew
on web openssl x509 -in /etc/letsencrypt/live/www.shop.test/cert.pem -noout -serial | tee ~/example/second.txt
sudo systemctl enable --now certbot@web.timer
