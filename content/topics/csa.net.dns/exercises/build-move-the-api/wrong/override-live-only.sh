# Wrong: the move is right, but the office's private address is given to
# the running resolver only, with unbound-control, and its
# /etc/unbound/unbound.conf is left as it was: the next restart of the
# resolver, or of the office, brings the public address back.
ttl_at() { on office dig +norecurse +noall +answer @"$1" api.shop.test A | awk '{print $2}'; }
answer_at() { on office dig +short @"$1" api.shop.test A; }
# The monitor has started, and logged both servers giving out the old TTL.
log=/var/lib/lab/move.log
until grep ' ns1 api 203.0.113.41 60$' $log > /dev/null 2>&1 && grep ' ns2 api 203.0.113.41 60$' $log > /dev/null 2>&1; do sleep 1; done
on ns1 sed -i -e 's/^api .*/api    5 IN A     203.0.113.41/' -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
until [ "$(ttl_at 198.51.100.13)" = 5 ] && [ "$(ttl_at 198.51.100.14)" = 5 ]; do sleep 1; done
sleep 70
on ns1 sed -i -e 's/^api .*/api    5 IN A     203.0.113.51/' -e 's/2026111202/2026111203/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
on resolver unbound-control local_zone shop.test transparent
on resolver unbound-control local_data "api.shop.test. A 10.0.8.51"
for isp in 198.51.100.21 198.51.100.22 198.51.100.23; do
  until [ "$(answer_at "$isp")" = 203.0.113.51 ]; do sleep 1; done
done
sleep 10
on ns1 sed -i -e 's/^api .*/api 3600 IN A     203.0.113.51/' -e 's/2026111203/2026111204/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
until [ "$(ttl_at 198.51.100.13)" = 3600 ] && [ "$(ttl_at 198.51.100.14)" = 3600 ]; do sleep 1; done
