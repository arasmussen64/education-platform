# Wrong: signing is taken off the shop's zone (perhaps after an edit was
# refused) and ns1 restarted. ns1 now serves the zone unsigned, but test.
# still holds shop.test's DS record, so every resolver that checks
# signatures expects a signed zone, finds none, and answers SERVFAIL.
on ns1 sed -i -e '/dnssec-policy/d' -e '/inline-signing/d' -e '/key-directory/d' /etc/bind/named.conf.local
on ns1 sed -i -e 's/^api .*/api    5 IN A     203.0.113.51/' -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
sudo systemctl restart named@ns1
on resolver tee -a /etc/unbound/unbound.conf <<'EOF'
server:
  local-zone: "shop.test." transparent
  local-data: "api.shop.test. A 10.0.8.51"
EOF
sudo systemctl restart unbound@resolver
sleep 12
