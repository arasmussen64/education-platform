# Wrong: the TTL is lowered and the old one waited out, but the switch
# puts the new address in with a TTL of 3600 at once. If the new server
# turns out to be wrong, every resolver now keeps it for an hour: the move
# was over before it had been checked.
ttl_at() { on office dig +norecurse +noall +answer @"$1" api.shop.test A | awk '{print $2}'; }
on ns1 sed -i -e 's/^api .*/api    5 IN A     203.0.113.41/' -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
until [ "$(ttl_at 198.51.100.13)" = 5 ] && [ "$(ttl_at 198.51.100.14)" = 5 ]; do sleep 1; done
sleep 70
on ns1 sed -i -e 's/^api .*/api 3600 IN A     203.0.113.51/' -e 's/2026111202/2026111203/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
on resolver tee -a /etc/unbound/unbound.conf <<'EOF'
server:
  local-zone: "shop.test." transparent
  local-data: "api.shop.test. A 10.0.8.51"
EOF
sudo systemctl restart unbound@resolver
until [ "$(ttl_at 198.51.100.13)" = 3600 ] && [ "$(ttl_at 198.51.100.14)" = 3600 ]; do sleep 1; done
sleep 15
