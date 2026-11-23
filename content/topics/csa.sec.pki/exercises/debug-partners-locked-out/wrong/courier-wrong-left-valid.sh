# Wrong: the courier gets a new certificate, and the one for a name the
# CA may not vouch for stays valid in the CA's database.
sudo systemctl enable --now crl-fetch@web.timer
sudo systemctl start crl-fetch@web.service
sleep 1
on web sh -c 'cat /home/learner/shop-pki/partners-2026.pem /home/learner/shop-pki/partners-2025.pem /home/learner/shop-pki/root.pem > /etc/nginx/tls/partners-bundle.pem'
on web nginx -t
sudo systemctl reload nginx@web
on courier openssl req -new -key /etc/partner/courier.key -subj "/CN=courier.partners.shop.test" -addext "subjectAltName=DNS:courier.partners.shop.test" -out /home/learner/transfer/courier.csr
on ca openssl ca -batch -config /etc/shop-ca/2026/ca.cnf -extensions partner -in /home/learner/transfer/courier.csr -out /home/learner/transfer/courier.pem
on courier cp /home/learner/transfer/courier.pem /etc/partner/courier.pem
sudo systemctl start crl-publish@ca.service
sudo systemctl start crl-fetch@web.service
sleep 1
