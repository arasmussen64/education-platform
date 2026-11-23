# Wrong: web checks CRLs, and fetched them before the courier's certificate
# was revoked. The CA then revoked it and published a new CRL, and the new
# file was copied to web by hand, but nginx was never told to read it, and
# no timer fetches. nginx goes on using the list it loaded, and the courier
# still gets in.
on courier openssl req -new -key /etc/partner/courier.key -subj "/CN=courier.partners.shop.test" -addext "subjectAltName=DNS:courier.partners.shop.test" -out /home/learner/transfer/courier.csr
on ca openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions partner -in /home/learner/transfer/courier.csr -out /home/learner/transfer/courier.pem
on courier cp /home/learner/transfer/courier.pem /etc/partner/courier.pem
openssl req -new -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -keyout ~/transfer/example.key -subj "/CN=www.example.test" -addext "subjectAltName=DNS:www.example.test" -out ~/transfer/example.csr
on ca openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions partner -in /home/learner/transfer/example.csr -out /home/learner/transfer/example.pem
on ca openssl ca -config /etc/shop-ca/ca.cnf -revoke /home/learner/transfer/example.pem -crl_reason superseded
on web sed -i 's/# if (/if (/' /etc/nginx/sites-available/partner-api
on ca openssl ca -config /etc/shop-ca/ca.cnf -gencrl -crlhours 2 -out /etc/shop-ca/public/partners.crl
on office curl -s http://crl.shop.test/partners.crl > ~/example/before.crl
on web sed -i 's/# ssl_crl/ssl_crl/' /etc/nginx/sites-available/partner-api
on web /usr/local/bin/fetch-crls && sleep 1
on ca openssl ca -config /etc/shop-ca/ca.cnf -revoke /home/learner/transfer/courier.pem -crl_reason keyCompromise
on ca openssl ca -config /etc/shop-ca/ca.cnf -gencrl -crlhours 2 -out /etc/shop-ca/public/partners.crl
on office curl -s http://crl.shop.test/partners.crl > ~/example/after.crl
on web sh -c 'curl -s http://crl.shop.test/partners.crl http://crl.shop.test/root.crl > /etc/nginx/tls/crls.pem'
sudo systemctl enable --now crl-publish@ca.timer
