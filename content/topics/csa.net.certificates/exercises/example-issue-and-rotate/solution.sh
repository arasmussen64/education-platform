netlab show
mkdir -p ~/example
on office openssl s_client -connect www.shop.test:443 -servername www.shop.test -showcerts < /dev/null 2> /dev/null | grep -E '^ *[0-9] s:|^ *[iv]:|^Verify return code'
on office openssl s_client -connect www.shop.test:443 -servername www.shop.test < /dev/null 2> /dev/null | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
on web certbot certonly --server https://ca.shop.test:9000/acme/acme/directory --webroot -w /var/www/html -d www.shop.test -m ops@shop.test --agree-tos --no-eff-email -n
on web ls -l /etc/letsencrypt/live/www.shop.test/
on web openssl x509 -in /etc/letsencrypt/live/www.shop.test/cert.pem -noout -subject -issuer -dates -ext subjectAltName,extendedKeyUsage
on web sed -i 's#/etc/nginx/tls/www.shop.test/#/etc/letsencrypt/live/www.shop.test/#' /etc/nginx/sites-available/shop
on web grep ssl_certificate /etc/nginx/sites-available/shop
on web nginx -t && sudo systemctl reload nginx@web && sleep 1
on office openssl s_client -connect www.shop.test:443 -servername www.shop.test < /dev/null 2> /dev/null | openssl x509 -noout -serial -dates | tee ~/example/first.txt
on web certbot reconfigure --cert-name www.shop.test --deploy-hook 'systemctl reload nginx@web' -n
on web grep -E '^(renew_hook|authenticator|webroot_path)' /etc/letsencrypt/renewal/www.shop.test.conf
on web certbot renew --cert-name www.shop.test --force-renewal --no-random-sleep-on-renew
on web ls -l /etc/letsencrypt/live/www.shop.test/ /etc/letsencrypt/archive/www.shop.test/
sleep 1; on office openssl s_client -connect www.shop.test:443 -servername www.shop.test < /dev/null 2> /dev/null | openssl x509 -noout -serial -dates | tee ~/example/second.txt
sudo systemctl enable --now certbot@web.timer
systemctl list-timers certbot@web.timer --no-pager
ls ~/example
