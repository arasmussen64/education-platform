# Wrong: the file nginx on web reads holds the partners' CA's CRL and not
# the root's. nginx wants a CRL from every CA in a client's chain, so
# without the root's it can't check the partners' CA's own certificate, and
# it refuses every partner, the warehouse included.
on courier openssl req -new -key /etc/partner/courier.key -subj "/CN=courier.partners.shop.test" -addext "subjectAltName=DNS:courier.partners.shop.test" -out /home/learner/transfer/courier.csr
on ca openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions partner -in /home/learner/transfer/courier.csr -out /home/learner/transfer/courier.pem
on courier cp /home/learner/transfer/courier.pem /etc/partner/courier.pem
openssl req -new -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -keyout ~/transfer/example.key -subj "/CN=www.example.test" -addext "subjectAltName=DNS:www.example.test" -out ~/transfer/example.csr
on ca openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions partner -in /home/learner/transfer/example.csr -out /home/learner/transfer/example.pem
on ca openssl ca -config /etc/shop-ca/ca.cnf -revoke /home/learner/transfer/example.pem -crl_reason superseded
on web sed -i 's/# if (/if (/' /etc/nginx/sites-available/partner-api
on ca openssl ca -config /etc/shop-ca/ca.cnf -gencrl -crlhours 2 -out /etc/shop-ca/public/partners.crl
on office curl -s http://crl.shop.test/partners.crl > ~/example/before.crl
on ca openssl ca -config /etc/shop-ca/ca.cnf -revoke /home/learner/transfer/courier.pem -crl_reason keyCompromise
on ca openssl ca -config /etc/shop-ca/ca.cnf -gencrl -crlhours 2 -out /etc/shop-ca/public/partners.crl
on office curl -s http://crl.shop.test/partners.crl > ~/example/after.crl
on web sed -i 's/# ssl_crl/ssl_crl/' /etc/nginx/sites-available/partner-api
on web sh -c 'curl -s http://crl.shop.test/partners.crl > /etc/nginx/tls/crls.pem'
on web nginx -t && sudo systemctl reload nginx@web && sleep 1
sudo systemctl enable --now crl-publish@ca.timer
