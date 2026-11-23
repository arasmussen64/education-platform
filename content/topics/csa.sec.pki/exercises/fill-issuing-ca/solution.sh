# The reference: each ___ filled in, here with sed -i, which edits a file in
# place (in the lab, nano does it by hand), then the script run.
#   - pathlen:0: the issuing CA is a CA, and no CA may stand below it;
#   - keyCertSign, cRLSign: its key signs certificates and CRLs only;
#   - critical, permitted;DNS:.shop.test: its certificates are good only
#     for names under shop.test (a list of what is allowed, not of what
#     isn't), and a client that can't read the limit must refuse;
#   - the CRL's address and the OCSP responder's, which every certificate
#     it issues will carry.
on root sed -i -e 's/^basicConstraints       = critical, CA:TRUE, ___/basicConstraints       = critical, CA:TRUE, pathlen:0/' \
  -e 's/^keyUsage               = critical, ___/keyUsage               = critical, keyCertSign, cRLSign/' \
  -e 's/^nameConstraints        = ___/nameConstraints        = critical, permitted;DNS:.shop.test/' /etc/shop-ca/ca.cnf
on ca sed -i -e 's#^crlDistributionPoints  = URI:___#crlDistributionPoints  = URI:http://crl.shop.test/services.crl#' \
  -e 's#^authorityInfoAccess    = OCSP;URI:___#authorityInfoAccess    = OCSP;URI:http://ocsp.shop.test:8888#' /etc/shop-ca/ca.cnf
~/bin/make-services-ca
on office curl -s https://api.shop.test/orders | head -n 1 || echo "the office can't reach the API"
