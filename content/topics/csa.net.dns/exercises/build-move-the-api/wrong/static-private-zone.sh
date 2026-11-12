# Wrong: the move is right, but the office's private zone is static, so the
# office's resolver answers every name under shop.test itself: api gets
# its private address, and every other name in the zone vanishes in the
# office.
ttl_at() { on office dig +norecurse +noall +answer @"$1" api.shop.test A | awk '{print $2}'; }
answer_at() { on office dig +short @"$1" api.shop.test A; }
on ns1 sed -i -e 's/^api .*/api    5 IN A     203.0.113.41/' -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
until [ "$(ttl_at 198.51.100.13)" = 5 ] && [ "$(ttl_at 198.51.100.14)" = 5 ]; do sleep 1; done
sleep 70
on ns1 sed -i -e 's/^api .*/api    5 IN A     203.0.113.51/' -e 's/2026111202/2026111203/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
on resolver tee -a /etc/unbound/unbound.conf <<'EOF'
server:
  local-zone: "shop.test." static
  local-data: "api.shop.test. A 10.0.8.51"
EOF
sudo systemctl restart unbound@resolver
for isp in 198.51.100.21 198.51.100.22 198.51.100.23; do
  until [ "$(answer_at "$isp")" = 203.0.113.51 ]; do sleep 1; done
done
sleep 10
on ns1 sed -i -e 's/^api .*/api 3600 IN A     203.0.113.51/' -e 's/2026111203/2026111204/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
until [ "$(ttl_at 198.51.100.13)" = 3600 ] && [ "$(ttl_at 198.51.100.14)" = 3600 ]; do sleep 1; done
