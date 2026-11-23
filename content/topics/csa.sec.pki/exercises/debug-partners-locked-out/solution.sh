# The reference fix. What nginx on web logs changes as each fault goes.
#
# 1. The warehouse is refused with (21:unable to verify the first
#    certificate): its certificate comes from the CA of 2025, and the file
#    of CAs nginx trusts for clients holds only the CA of 2026 and the
#    root. Until the last certificate of the old CA has expired, both
#    issuing CAs belong in it.
on web sh -c 'cat /home/learner/shop-pki/partners-2026.pem /home/learner/shop-pki/partners-2025.pem /home/learner/shop-pki/root.pem > /etc/nginx/tls/partners-bundle.pem'
on web nginx -t
sudo systemctl reload nginx@web

# 2. Now the warehouse is refused with (12:CRL has expired): web's copy of
#    the CRLs ran out, and "systemctl list-timers" has no crl-fetch@web.timer
#    in it. The timer that fetches them was switched off. It is switched on
#    again, now and at every boot, and its service is run once by hand, so
#    that web has today's lists without waiting for the timer's first turn.
sudo systemctl enable --now crl-fetch@web.timer
sudo systemctl start crl-fetch@web.service
sleep 1

# 3. The courier is refused with (47:permitted subtree violation): its
#    certificate is for courier.partner.test, and the CA may only vouch for
#    names under partners.shop.test. The CA copied the name from the
#    request. A new request, made on courier with the key it has, for the
#    right name; a new certificate from the CA of 2026; and the wrong one
#    revoked, since the CA should never have issued it.
on courier cp /etc/partner/courier.pem /home/learner/transfer/courier-wrong.pem
on courier openssl req -new -key /etc/partner/courier.key -subj "/CN=courier.partners.shop.test" -addext "subjectAltName=DNS:courier.partners.shop.test" -out /home/learner/transfer/courier.csr
on ca openssl ca -batch -config /etc/shop-ca/2026/ca.cnf -extensions partner -in /home/learner/transfer/courier.csr -out /home/learner/transfer/courier.pem
on courier cp /home/learner/transfer/courier.pem /etc/partner/courier.pem
on ca openssl ca -config /etc/shop-ca/2026/ca.cnf -revoke /home/learner/transfer/courier-wrong.pem -crl_reason superseded
sudo systemctl start crl-publish@ca.service
sudo systemctl start crl-fetch@web.service
sleep 1
on depot curl -s -o /dev/null -w 'the warehouse: %{http_code}\n' --cert /etc/partner/warehouse.pem --key /etc/partner/warehouse.key https://api.shop.test/orders
on courier curl -s -o /dev/null -w 'the courier: %{http_code}\n' --cert /etc/partner/courier.pem --key /etc/partner/courier.key https://api.shop.test/orders
