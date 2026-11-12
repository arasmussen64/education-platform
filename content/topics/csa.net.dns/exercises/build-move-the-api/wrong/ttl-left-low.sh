# Wrong: the move is right, but the TTL is never raised again. Every
# resolver then asks the shop's servers about api.shop.test every 5
# seconds, for ever, and an outage of the servers is felt within seconds.
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
  local-zone: "shop.test." transparent
  local-data: "api.shop.test. A 10.0.8.51"
EOF
sudo systemctl restart unbound@resolver
for isp in 198.51.100.21 198.51.100.22 198.51.100.23; do
  until [ "$(answer_at "$isp")" = 203.0.113.51 ]; do sleep 1; done
done
sleep 10
