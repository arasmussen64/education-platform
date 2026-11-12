# Wrong: the DS record is made from ns-eu's key, and then ns-eu's keys are
# thrown away and made again (its key folder emptied, BIND restarted). The
# DS in shop.test now matches no key ns-eu has, so every resolver that
# checks signatures answers SERVFAIL for the whole European site.
on ns-eu sed -i -e 's/( \.\.\. 3600/( 2026111201 3600/' -e 's/^@        IN NS    \.\.\.$/@        IN NS    ns-eu/' \
  -e 's/^ns-eu    IN A     \.\.\.$/ns-eu    IN A     198.51.100.15/' /etc/bind/db.eu.shop.test
on ns-eu sed -i -e 's|file "\.\.\.";|file "/etc/bind/db.eu.shop.test";|' -e 's/dnssec-policy \.\.\.;/dnssec-policy default;/' /etc/bind/named.conf.local
sudo systemctl reset-failed named@ns-eu
sudo systemctl restart named@ns-eu
until on office dig +norecurse +short @198.51.100.15 eu.shop.test DNSKEY | grep '^257 ' > /dev/null; do sleep 1; done
ds=$(on office dig +norecurse +noall +answer @198.51.100.15 eu.shop.test DNSKEY | dnssec-dsfromkey -2 -f - eu.shop.test)
on ns1 sed -i -e 's/^;eu       IN NS    \.\.\.$/eu       IN NS    ns-eu.eu/' -e 's/^;ns-eu\.eu IN A     \.\.\.$/ns-eu.eu IN A     198.51.100.15/' \
  -e "s/^;eu       IN DS    \.\.\.$/$ds/" -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
sudo systemctl stop named@ns-eu
on ns-eu bash -c 'rm -f /etc/bind/keys/* /etc/bind/db.eu.shop.test.signed* /etc/bind/db.eu.shop.test.jbk'
sudo systemctl start named@ns-eu
until on office dig +norecurse +short @198.51.100.15 eu.shop.test DNSKEY | grep '^257 ' > /dev/null; do sleep 1; done
sleep 2
