# The reference fill-in. A learner edits each file with nano; here each gap
# is filled with sed, which replaces one pattern with another (s/old/new/).
# 1. ns-eu's zone: a serial, its own name server, and that server's address.
on ns-eu sed -i -e 's/( \.\.\. 3600/( 2026111201 3600/' -e 's/^@        IN NS    \.\.\.$/@        IN NS    ns-eu/' \
  -e 's/^ns-eu    IN A     \.\.\.$/ns-eu    IN A     198.51.100.15/' /etc/bind/db.eu.shop.test
# 2. ns-eu's zone settings: the zone file, and BIND's default DNSSEC policy.
on ns-eu sed -i -e 's|file "\.\.\.";|file "/etc/bind/db.eu.shop.test";|' -e 's/dnssec-policy \.\.\.;/dnssec-policy default;/' /etc/bind/named.conf.local
on ns-eu named-checkconf
on ns-eu named-checkzone eu.shop.test /etc/bind/db.eu.shop.test
# named@ns-eu failed at boot, five times in a few seconds, and systemd won't
# start a service again that soon after such a run of failures:
# reset-failed clears that (minutes later, a plain restart would do).
sudo systemctl reset-failed named@ns-eu
sudo systemctl restart named@ns-eu
# BIND makes the zone's key at its first start and publishes it (DNSKEY).
until on office dig +norecurse +short @198.51.100.15 eu.shop.test DNSKEY | grep '^257 ' > /dev/null; do sleep 1; done

# 3. The delegation in shop.test: NS, glue, and the DS record, which
# dnssec-dsfromkey makes from the key ns-eu publishes; then a higher serial.
ds=$(on office dig +norecurse +noall +answer @198.51.100.15 eu.shop.test DNSKEY | dnssec-dsfromkey -2 -f - eu.shop.test)
echo "$ds"
on ns1 sed -i -e 's/^;eu       IN NS    \.\.\.$/eu       IN NS    ns-eu.eu/' -e 's/^;ns-eu\.eu IN A     \.\.\.$/ns-eu.eu IN A     198.51.100.15/' \
  -e "s/^;eu       IN DS    \.\.\.$/$ds/" -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
# ns1 tells ns2 about the change about 5 seconds later (BIND waits that long
# before it sends a NOTIFY), and ns2 copies the zone: wait for ns2's referral.
until on office dig +norecurse @198.51.100.14 www.eu.shop.test | grep 'ns-eu' > /dev/null; do sleep 1; done

# 4. The trail, from ns1 to ns-eu, and through a public resolver that
# checks signatures: the answer, with ad.
on office dig @198.51.100.13 +norecurse www.eu.shop.test
on isp1 dig www.eu.shop.test
