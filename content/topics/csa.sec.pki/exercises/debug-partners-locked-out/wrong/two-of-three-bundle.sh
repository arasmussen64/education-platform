# Wrong: two of the three faults fixed. nginx still trusts only the CA of
# 2026 and the root, so the warehouse, whose certificate the CA of 2025
# issued, is still refused.
sudo systemctl enable --now crl-fetch@web.timer
sudo systemctl start crl-fetch@web.service
sleep 1
on courier cp /etc/partner/courier.pem /home/learner/transfer/courier-wrong.pem
on courier openssl req -new -key /etc/partner/courier.key -subj "/CN=courier.partners.shop.test" -addext "subjectAltName=DNS:courier.partners.shop.test" -out /home/learner/transfer/courier.csr
on ca openssl ca -batch -config /etc/shop-ca/2026/ca.cnf -extensions partner -in /home/learner/transfer/courier.csr -out /home/learner/transfer/courier.pem
on courier cp /home/learner/transfer/courier.pem /etc/partner/courier.pem
on ca openssl ca -config /etc/shop-ca/2026/ca.cnf -revoke /home/learner/transfer/courier-wrong.pem -crl_reason superseded
sudo systemctl start crl-publish@ca.service
sudo systemctl start crl-fetch@web.service
sleep 1
