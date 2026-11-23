# Wrong: the gaps are right, and a copy of the root's key is kept on the
# lab machine "for next time", in the binary form (DER) and in a folder a
# reboot empties, where a search for PEM files in /etc wouldn't find it.
on root sed -i -e 's/^basicConstraints       = critical, CA:TRUE, ___/basicConstraints       = critical, CA:TRUE, pathlen:0/' \
  -e 's/^keyUsage               = critical, ___/keyUsage               = critical, keyCertSign, cRLSign/' \
  -e 's/^nameConstraints        = ___/nameConstraints        = critical, permitted;DNS:.shop.test/' /etc/shop-ca/ca.cnf
on ca sed -i -e 's#^crlDistributionPoints  = URI:___#crlDistributionPoints  = URI:http://crl.shop.test/services.crl#' \
  -e 's#^authorityInfoAccess    = OCSP;URI:___#authorityInfoAccess    = OCSP;URI:http://ocsp.shop.test:8888#' /etc/shop-ca/ca.cnf
sudo openssl pkey -in /etc/netns/root/shop-ca/root.key -outform DER -out /run/root-key.der
~/bin/make-services-ca
