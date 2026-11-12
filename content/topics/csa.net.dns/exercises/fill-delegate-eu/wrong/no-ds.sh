# Wrong: the delegation and glue are in, but not the DS record. Resolvers
# find eu.shop.test, but shop.test says nothing about its key, so its
# answers are never checked: an island of signatures nobody can trust.
on ns-eu sed -i -e 's/( \.\.\. 3600/( 2026111201 3600/' -e 's/^@        IN NS    \.\.\.$/@        IN NS    ns-eu/' \
  -e 's/^ns-eu    IN A     \.\.\.$/ns-eu    IN A     198.51.100.15/' /etc/bind/db.eu.shop.test
on ns-eu sed -i -e 's|file "\.\.\.";|file "/etc/bind/db.eu.shop.test";|' -e 's/dnssec-policy \.\.\.;/dnssec-policy default;/' /etc/bind/named.conf.local
sudo systemctl reset-failed named@ns-eu
sudo systemctl restart named@ns-eu
on ns1 sed -i -e 's/^;eu       IN NS    \.\.\.$/eu       IN NS    ns-eu.eu/' -e 's/^;ns-eu\.eu IN A     \.\.\.$/ns-eu.eu IN A     198.51.100.15/' \
  -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
sleep 8
