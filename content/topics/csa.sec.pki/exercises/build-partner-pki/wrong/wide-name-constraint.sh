# Wrong: the name constraint permits everything under shop.test, so the
# partners' CA can vouch for the shop's own names too.
# 1. The root, on the machine with no network: a key that stays there, and
#    a certificate it signs itself.
on root openssl ecparam -name prime256v1 -genkey -noout -out /etc/shop-ca/root.key
on root openssl req -x509 -new -config /etc/shop-ca/ca.cnf -extensions v3_root -key /etc/shop-ca/root.key -days 7300 -out /etc/shop-ca/root.pem

# 2. The partners' CA: its key and request are made on ca, and the request
#    is carried to root. The root's settings gain the section that limits
#    this CA: no CA below it, names under partners.shop.test only, client
#    certificates only. The root signs it, makes its own CRL, and both are
#    carried back with the root's certificate.
on ca openssl ecparam -name prime256v1 -genkey -noout -out /etc/shop-ca/partners.key
on ca openssl req -new -key /etc/shop-ca/partners.key -subj "/CN=Shop Partners CA" -out /home/learner/transfer/partners.csr
on root tee -a /etc/shop-ca/ca.cnf > /dev/null <<'EOF'

[ v3_partners_ca ]
basicConstraints       = critical, CA:TRUE, pathlen:0
keyUsage               = critical, keyCertSign, cRLSign
nameConstraints        = critical, permitted;DNS:.shop.test
extendedKeyUsage       = clientAuth
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid
EOF
on root openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions v3_partners_ca -in /home/learner/transfer/partners.csr -out /home/learner/transfer/partners.pem
on root openssl ca -config /etc/shop-ca/ca.cnf -gencrl -crldays 180 -out /home/learner/transfer/root.crl
on root cp /etc/shop-ca/root.pem /home/learner/transfer/root.pem
on ca cp /home/learner/transfer/partners.pem /etc/shop-ca/partners.pem
on ca cp /home/learner/transfer/root.pem /home/learner/transfer/root.crl /home/learner/transfer/partners.pem /etc/shop-ca/public/

# 3. What the partners' CA writes into every certificate, and the two
#    partners' certificates, each from a request made where its key is.
on ca tee -a /etc/shop-ca/ca.cnf > /dev/null <<'EOF'

[ partner ]
basicConstraints       = critical, CA:FALSE
keyUsage               = critical, digitalSignature
extendedKeyUsage       = clientAuth
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid
crlDistributionPoints  = URI:http://crl.shop.test/partners.crl
authorityInfoAccess    = OCSP;URI:http://ocsp.shop.test:8888
EOF
on depot openssl req -new -key /etc/partner/warehouse.key -subj "/CN=warehouse.partners.shop.test" -addext "subjectAltName=DNS:warehouse.partners.shop.test" -out /home/learner/transfer/warehouse.csr
on ca openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions partner -in /home/learner/transfer/warehouse.csr -out /home/learner/transfer/warehouse.pem
on depot cp /home/learner/transfer/warehouse.pem /etc/partner/warehouse.pem
on courier openssl req -new -key /etc/partner/courier.key -subj "/CN=courier.partners.shop.test" -addext "subjectAltName=DNS:courier.partners.shop.test" -out /home/learner/transfer/courier.csr
on ca openssl ca -batch -config /etc/shop-ca/ca.cnf -extensions partner -in /home/learner/transfer/courier.csr -out /home/learner/transfer/courier.pem
on courier cp /home/learner/transfer/courier.pem /etc/partner/courier.pem

# 4. The CA publishes: a script that makes the next CRL, good for 2 hours,
#    a timer that runs it every hour and after every boot, and the OCSP
#    responder.
sudo tee /usr/local/bin/publish-crl > /dev/null <<'EOF'
#!/bin/bash
set -e
openssl ca -config /etc/shop-ca/ca.cnf -gencrl -crlhours 2 -out /etc/shop-ca/public/partners.crl.new
mv /etc/shop-ca/public/partners.crl.new /etc/shop-ca/public/partners.crl
EOF
sudo chmod +x /usr/local/bin/publish-crl
sudo tee /etc/systemd/system/crl-publish@.timer > /dev/null <<'EOF'
[Unit]
Description=Publish the CA's CRL on %i every hour

[Timer]
OnBootSec=30s
OnUnitActiveSec=1h

[Install]
WantedBy=timers.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now crl-publish@ca.timer
sudo systemctl enable --now ocsp-responder@ca

# 5. The API: client certificates required, from a chain that ends at the
#    root, checked against both CAs' CRLs; a script that fetches the CRLs
#    and reloads nginx, and a timer that runs it every half hour.
on web sh -c 'cat /home/learner/transfer/partners.pem /home/learner/transfer/root.pem > /etc/nginx/tls/partners-bundle.pem'
on web sed -i 's#^    root /srv/www/api;#    ssl_client_certificate /etc/nginx/tls/partners-bundle.pem;\n    ssl_verify_client on;\n    ssl_crl /etc/nginx/tls/crls.pem;\n    root /srv/www/api;#' /etc/nginx/sites-available/partner-api
sudo tee /usr/local/bin/fetch-crls > /dev/null <<'EOF'
#!/bin/bash
set -e
new=$(mktemp)
curl -fsS --max-time 10 http://crl.shop.test/partners.crl http://crl.shop.test/root.crl > "$new"
cat "$new" > /etc/nginx/tls/crls.pem
rm -f "$new"
systemctl reload nginx@web
EOF
sudo chmod +x /usr/local/bin/fetch-crls
sudo tee /etc/systemd/system/crl-fetch@.timer > /dev/null <<'EOF'
[Unit]
Description=Fetch the CA's CRLs on %i every half hour

[Timer]
OnBootSec=45s
OnUnitActiveSec=30min

[Install]
WantedBy=timers.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now crl-fetch@web.timer
sleep 2

# 6. The courier's laptop has gone: revoke its certificate, publish, fetch.
on ca openssl ca -config /etc/shop-ca/ca.cnf -revoke /home/learner/transfer/courier.pem -crl_reason keyCompromise
sudo systemctl start crl-publish@ca.service
sudo systemctl start crl-fetch@web.service
sleep 1
on depot curl -s -o /dev/null -w 'the warehouse: %{http_code}\n' --cert /etc/partner/warehouse.pem --key /etc/partner/warehouse.key https://api.shop.test/orders
on courier curl -s -o /dev/null -w 'the courier: %{http_code}\n' --cert /etc/partner/courier.pem --key /etc/partner/courier.key https://api.shop.test/orders
