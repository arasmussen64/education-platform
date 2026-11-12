# Wrong: the certificate issued and served, then renewed with no hook to
# reload nginx: certbot's files change, the running nginx keeps the old
# certificate, and the two serials saved are the same one.
mkdir -p ~/example
on web certbot certonly --server https://ca.shop.test:9000/acme/acme/directory --webroot -w /var/www/html -d www.shop.test -m ops@shop.test --agree-tos --no-eff-email -n
on web sed -i 's#/etc/nginx/tls/www.shop.test/#/etc/letsencrypt/live/www.shop.test/#' /etc/nginx/sites-available/shop
on web nginx -t && sudo systemctl reload nginx@web && sleep 1
on office openssl s_client -connect www.shop.test:443 -servername www.shop.test < /dev/null 2> /dev/null | openssl x509 -noout -serial -dates | tee ~/example/first.txt
on web certbot renew --cert-name www.shop.test --force-renewal --no-random-sleep-on-renew
sleep 1; on office openssl s_client -connect www.shop.test:443 -servername www.shop.test < /dev/null 2> /dev/null | openssl x509 -noout -serial -dates | tee ~/example/second.txt
sudo systemctl enable --now certbot@web.timer
