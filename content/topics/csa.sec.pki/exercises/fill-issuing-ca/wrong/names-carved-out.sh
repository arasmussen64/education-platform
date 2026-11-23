# Wrong: the name constraint lists a name the CA may not sign for, instead
# of the names it may. Every name nobody thought to exclude still verifies.
on root sed -i -e 's/^basicConstraints       = critical, CA:TRUE, ___/basicConstraints       = critical, CA:TRUE, pathlen:0/' \
  -e 's/^keyUsage               = critical, ___/keyUsage               = critical, keyCertSign, cRLSign/' \
  -e 's/^nameConstraints        = ___/nameConstraints        = critical, excluded;DNS:.example.test/' /etc/shop-ca/ca.cnf
on ca sed -i -e 's#^crlDistributionPoints  = URI:___#crlDistributionPoints  = URI:http://crl.shop.test/services.crl#' \
  -e 's#^authorityInfoAccess    = OCSP;URI:___#authorityInfoAccess    = OCSP;URI:http://ocsp.shop.test:8888#' /etc/shop-ca/ca.cnf
~/bin/make-services-ca
