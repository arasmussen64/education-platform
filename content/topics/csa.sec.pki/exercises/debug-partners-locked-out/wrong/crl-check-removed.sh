# Wrong: the expired CRL is dealt with by taking the ssl_crl line out of
# the site. Partners get in again, and so does the florist, whose
# certificate was revoked last week.
on web sed -i '/ssl_crl/d' /etc/nginx/sites-available/partner-api
on web sh -c 'cat /home/learner/shop-pki/partners-2026.pem /home/learner/shop-pki/partners-2025.pem /home/learner/shop-pki/root.pem > /etc/nginx/tls/partners-bundle.pem'
on web nginx -t
sudo systemctl reload nginx@web
on courier cp /etc/partner/courier.pem /home/learner/transfer/courier-wrong.pem
on courier openssl req -new -key /etc/partner/courier.key -subj "/CN=courier.partners.shop.test" -addext "subjectAltName=DNS:courier.partners.shop.test" -out /home/learner/transfer/courier.csr
on ca openssl ca -batch -config /etc/shop-ca/2026/ca.cnf -extensions partner -in /home/learner/transfer/courier.csr -out /home/learner/transfer/courier.pem
on courier cp /home/learner/transfer/courier.pem /etc/partner/courier.pem
on ca openssl ca -config /etc/shop-ca/2026/ca.cnf -revoke /home/learner/transfer/courier-wrong.pem -crl_reason superseded
sudo systemctl start crl-publish@ca.service
sleep 1
