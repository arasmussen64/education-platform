# Wrong: nginx's file of trusted CAs is left alone, and the warehouse is
# given a new certificate from the CA of 2026 instead. The warehouse's
# certificate was to stay, and every other partner of the old CA is
# still locked out.
sudo systemctl enable --now crl-fetch@web.timer
sudo systemctl start crl-fetch@web.service
sleep 1
on depot openssl req -new -key /etc/partner/warehouse.key -subj "/CN=warehouse.partners.shop.test" -addext "subjectAltName=DNS:warehouse.partners.shop.test" -out /home/learner/transfer/warehouse.csr
on ca openssl ca -batch -config /etc/shop-ca/2026/ca.cnf -extensions partner -in /home/learner/transfer/warehouse.csr -out /home/learner/transfer/warehouse.pem
on depot cp /home/learner/transfer/warehouse.pem /etc/partner/warehouse.pem
on courier cp /etc/partner/courier.pem /home/learner/transfer/courier-wrong.pem
on courier openssl req -new -key /etc/partner/courier.key -subj "/CN=courier.partners.shop.test" -addext "subjectAltName=DNS:courier.partners.shop.test" -out /home/learner/transfer/courier.csr
on ca openssl ca -batch -config /etc/shop-ca/2026/ca.cnf -extensions partner -in /home/learner/transfer/courier.csr -out /home/learner/transfer/courier.pem
on courier cp /home/learner/transfer/courier.pem /etc/partner/courier.pem
on ca openssl ca -config /etc/shop-ca/2026/ca.cnf -revoke /home/learner/transfer/courier-wrong.pem -crl_reason superseded
sudo systemctl start crl-publish@ca.service
sudo systemctl start crl-fetch@web.service
sleep 1
