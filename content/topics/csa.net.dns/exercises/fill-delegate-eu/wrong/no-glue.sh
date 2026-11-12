# Wrong: the delegation names ns-eu.eu.shop.test but gives no address for
# it (no glue). The name is inside the zone being delegated, so a resolver
# can only find its address by asking ns-eu itself: it never can.
on ns-eu sed -i -e 's/( \.\.\. 3600/( 2026111201 3600/' -e 's/^@        IN NS    \.\.\.$/@        IN NS    ns-eu/' \
  -e 's/^ns-eu    IN A     \.\.\.$/ns-eu    IN A     198.51.100.15/' /etc/bind/db.eu.shop.test
on ns-eu sed -i -e 's|file "\.\.\.";|file "/etc/bind/db.eu.shop.test";|' -e 's/dnssec-policy \.\.\.;/dnssec-policy default;/' /etc/bind/named.conf.local
sudo systemctl reset-failed named@ns-eu
sudo systemctl restart named@ns-eu
until on office dig +norecurse +short @198.51.100.15 eu.shop.test DNSKEY | grep '^257 ' > /dev/null; do sleep 1; done
ds=$(on office dig +norecurse +noall +answer @198.51.100.15 eu.shop.test DNSKEY | dnssec-dsfromkey -2 -f - eu.shop.test)
on ns1 sed -i -e 's/^;eu       IN NS    \.\.\.$/eu       IN NS    ns-eu.eu/' \
  -e "s/^;eu       IN DS    \.\.\.$/$ds/" -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
sleep 8
