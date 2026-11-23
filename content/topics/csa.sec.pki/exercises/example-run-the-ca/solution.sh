netlab show
on root ip -brief address
on ca cat /etc/shop-ca/ca.cnf
on ca cat /etc/shop-ca/index.txt
openssl x509 -in ~/shop-pki/partners.pem -noout -subject -issuer -ext basicConstraints,nameConstraints,extendedKeyUsage
on courier openssl req -new -key /etc/partner/courier.key -subj "/CN=courier.partners.shop.test" -addext "subjectAltName=DNS:courier.partners.shop.test" -out /home/learner/transfer/courier.csr
on ca openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions partner -in /home/learner/transfer/courier.csr -out /home/learner/transfer/courier.pem
on ca cat /etc/shop-ca/index.txt
on courier cp /home/learner/transfer/courier.pem /etc/partner/courier.pem
on courier openssl x509 -in /etc/partner/courier.pem -noout -subject -enddate -ext subjectAltName,extendedKeyUsage,crlDistributionPoints,authorityInfoAccess
on courier curl -s -o /dev/null -w '%{http_code}\n' --cert /etc/partner/courier.pem --key /etc/partner/courier.key https://api.shop.test/orders
openssl req -new -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -keyout ~/transfer/example.key -subj "/CN=www.example.test" -addext "subjectAltName=DNS:www.example.test" -out ~/transfer/example.csr
on ca openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions partner -in /home/learner/transfer/example.csr -out /home/learner/transfer/example.pem
openssl verify -CAfile ~/shop-pki/root.pem -untrusted ~/shop-pki/partners.pem ~/transfer/example.pem || true
on ca openssl ca -config /etc/shop-ca/ca.cnf -revoke /home/learner/transfer/example.pem -crl_reason superseded
on office curl -s -o /dev/null -w '%{http_code}\n' --cert /home/learner/staff/ana-chain.pem --key /home/learner/staff/ana.key https://api.shop.test/orders
on web sed -i 's/# if (/if (/' /etc/nginx/sites-available/partner-api
on web nginx -t && sudo systemctl reload nginx@web && sleep 1
on office curl -s -o /dev/null -w '%{http_code}\n' --cert /home/learner/staff/ana-chain.pem --key /home/learner/staff/ana.key https://api.shop.test/orders
on ca openssl ca -config /etc/shop-ca/ca.cnf -gencrl -crlhours 2 -out /etc/shop-ca/public/partners.crl
on office curl -s http://crl.shop.test/partners.crl > ~/example/before.crl
openssl crl -in ~/example/before.crl -noout -lastupdate -nextupdate -crlnumber
on ca openssl ca -config /etc/shop-ca/ca.cnf -revoke /home/learner/transfer/courier.pem -crl_reason keyCompromise
on ca cat /etc/shop-ca/index.txt
openssl verify -crl_check -CAfile ~/shop-pki/root.pem -untrusted ~/shop-pki/partners.pem -CRLfile ~/example/before.crl ~/transfer/courier.pem
on ca openssl ca -config /etc/shop-ca/ca.cnf -gencrl -crlhours 2 -out /etc/shop-ca/public/partners.crl
on office curl -s http://crl.shop.test/partners.crl > ~/example/after.crl
openssl verify -crl_check -CAfile ~/shop-pki/root.pem -untrusted ~/shop-pki/partners.pem -CRLfile ~/example/after.crl ~/transfer/courier.pem || true
on office openssl ocsp -issuer /home/learner/shop-pki/partners.pem -CAfile /home/learner/shop-pki/root.pem -cert /home/learner/transfer/courier.pem -url http://ocsp.shop.test:8888
on office openssl ocsp -issuer /home/learner/shop-pki/partners.pem -CAfile /home/learner/shop-pki/root.pem -cert /home/learner/transfer/courier.pem -url http://ocsp.shop.test:8888
on courier curl -s -o /dev/null -w '%{http_code}\n' --cert /etc/partner/courier.pem --key /etc/partner/courier.key https://api.shop.test/orders
cat /usr/local/bin/fetch-crls
on web sed -i 's/# ssl_crl/ssl_crl/' /etc/nginx/sites-available/partner-api
on web /usr/local/bin/fetch-crls && sleep 1
on courier curl -s --cert /etc/partner/courier.pem --key /etc/partner/courier.key https://api.shop.test/orders | grep title
on web grep 'verify error' /var/log/nginx/error.log | tail -n 1
on depot curl -s -o /dev/null -w '%{http_code}\n' --cert /etc/partner/warehouse.pem --key /etc/partner/warehouse.key https://api.shop.test/orders
systemctl cat crl-publish@ca.timer crl-fetch@web.timer --no-pager
sudo systemctl enable --now crl-publish@ca.timer crl-fetch@web.timer
systemctl list-timers 'crl-*' --no-pager
