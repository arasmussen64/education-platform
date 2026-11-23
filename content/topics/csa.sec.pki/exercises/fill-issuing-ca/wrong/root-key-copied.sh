# Wrong: the gaps are right, and the root's key is copied to ca "so the
# next issuing CA can be signed without the trip".
on root sed -i -e 's/^basicConstraints       = critical, CA:TRUE, ___/basicConstraints       = critical, CA:TRUE, pathlen:0/' \
  -e 's/^keyUsage               = critical, ___/keyUsage               = critical, keyCertSign, cRLSign/' \
  -e 's/^nameConstraints        = ___/nameConstraints        = critical, permitted;DNS:.shop.test/' /etc/shop-ca/ca.cnf
on ca sed -i -e 's#^crlDistributionPoints  = URI:___#crlDistributionPoints  = URI:http://crl.shop.test/services.crl#' \
  -e 's#^authorityInfoAccess    = OCSP;URI:___#authorityInfoAccess    = OCSP;URI:http://ocsp.shop.test:8888#' /etc/shop-ca/ca.cnf
on root cp /etc/shop-ca/root.key /home/learner/transfer/root.key
on ca cp /home/learner/transfer/root.key /etc/shop-ca/root.key
~/bin/make-services-ca
