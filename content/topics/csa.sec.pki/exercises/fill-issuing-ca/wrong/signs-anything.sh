# Wrong: the issuing CA's key usage adds digitalSignature, a use a CA's
# key was not to have.
on root sed -i -e 's/^basicConstraints       = critical, CA:TRUE, ___/basicConstraints       = critical, CA:TRUE, pathlen:0/' \
  -e 's/^keyUsage               = critical, ___/keyUsage               = critical, digitalSignature, keyCertSign, cRLSign/' \
  -e 's/^nameConstraints        = ___/nameConstraints        = critical, permitted;DNS:.shop.test/' /etc/shop-ca/ca.cnf
on ca sed -i -e 's#^crlDistributionPoints  = URI:___#crlDistributionPoints  = URI:http://crl.shop.test/services.crl#' \
  -e 's#^authorityInfoAccess    = OCSP;URI:___#authorityInfoAccess    = OCSP;URI:http://ocsp.shop.test:8888#' /etc/shop-ca/ca.cnf
~/bin/make-services-ca
