# Wrong: everything but the line that tests which CA issued a client's
# certificate. nginx trusts the root in its file, so it trusts every CA the
# root has signed, the staff's included. Today a staff laptop is turned away
# only because web holds no CRL from the staff's CA, which nobody decided
# and which the next person to "tidy up" the CRL file would undo.
on courier openssl req -new -key /etc/partner/courier.key -subj "/CN=courier.partners.shop.test" -addext "subjectAltName=DNS:courier.partners.shop.test" -out /home/learner/transfer/courier.csr
on ca openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions partner -in /home/learner/transfer/courier.csr -out /home/learner/transfer/courier.pem
on courier cp /home/learner/transfer/courier.pem /etc/partner/courier.pem
openssl req -new -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -keyout ~/transfer/example.key -subj "/CN=www.example.test" -addext "subjectAltName=DNS:www.example.test" -out ~/transfer/example.csr
on ca openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions partner -in /home/learner/transfer/example.csr -out /home/learner/transfer/example.pem
on ca openssl ca -config /etc/shop-ca/ca.cnf -revoke /home/learner/transfer/example.pem -crl_reason superseded
on ca openssl ca -config /etc/shop-ca/ca.cnf -gencrl -crlhours 2 -out /etc/shop-ca/public/partners.crl
on office curl -s http://crl.shop.test/partners.crl > ~/example/before.crl
on ca openssl ca -config /etc/shop-ca/ca.cnf -revoke /home/learner/transfer/courier.pem -crl_reason keyCompromise
on ca openssl ca -config /etc/shop-ca/ca.cnf -gencrl -crlhours 2 -out /etc/shop-ca/public/partners.crl
on office curl -s http://crl.shop.test/partners.crl > ~/example/after.crl
on web sed -i 's/# ssl_crl/ssl_crl/' /etc/nginx/sites-available/partner-api
on web /usr/local/bin/fetch-crls && sleep 1
sudo systemctl enable --now crl-publish@ca.timer crl-fetch@web.timer
