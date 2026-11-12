# The reference move, step by step. Each edit of the zone file is made here
# with sed (a learner uses nano): it sets api's line and raises the serial,
# and rndc reload makes ns1 load it; ns1 then tells ns2 at once.
# ttl_at SERVER: the TTL a server gives out for api.shop.test, asked directly.
ttl_at() { on office dig +norecurse +noall +answer @"$1" api.shop.test A | awk '{print $2}'; }
answer_at() { on office dig +short @"$1" api.shop.test A; }

# 1. Lower api's TTL from 60 to 5, with a higher serial.
on ns1 sed -i -e 's/^api .*/api    5 IN A     203.0.113.41/' -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
# The wait starts once both servers give out the new TTL.
until [ "$(ttl_at 198.51.100.13)" = 5 ] && [ "$(ttl_at 198.51.100.14)" = 5 ]; do sleep 1; done

# 2. Wait out the old TTL, 60 seconds, with a margin: every copy handed out
# with the old TTL has then expired.
sleep 70

# 3. Switch: the new address, still with the move's TTL of 5.
on ns1 sed -i -e 's/^api .*/api    5 IN A     203.0.113.51/' -e 's/2026111202/2026111203/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test

# The office's resolver answers api.shop.test with the new server's private
# address and resolves every other name normally (transparent). The second
# server: block adds to the first; tee -a appends the lines up to EOF.
on resolver tee -a /etc/unbound/unbound.conf <<'EOF'
server:
  local-zone: "shop.test." transparent
  local-data: "api.shop.test. A 10.0.8.51"
EOF
on resolver unbound-checkconf
sudo systemctl restart unbound@resolver

# 4. Check through every public resolver: within the TTL of 5 they all give
# out the new address.
for isp in 198.51.100.21 198.51.100.22 198.51.100.23; do
  until [ "$(answer_at "$isp")" = 203.0.113.51 ]; do sleep 1; done
done
sleep 10

# 5. The move is done: raise the TTL to 3600 again.
on ns1 sed -i -e 's/^api .*/api 3600 IN A     203.0.113.51/' -e 's/2026111203/2026111204/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
until [ "$(ttl_at 198.51.100.13)" = 3600 ] && [ "$(ttl_at 198.51.100.14)" = 3600 ]; do sleep 1; done
on office dig +short api.shop.test
