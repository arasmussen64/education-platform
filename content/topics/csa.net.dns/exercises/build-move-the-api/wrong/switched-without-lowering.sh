# Wrong: the address is changed and the TTL raised to 3600 in one edit,
# with no lowering and no wait. Resolvers that fetched the old address a
# moment before keep handing it out for up to its old TTL.
on ns1 sed -i -e 's/^api .*/api 3600 IN A     203.0.113.51/' -e 's/2026111201/2026111202/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
on resolver tee -a /etc/unbound/unbound.conf <<'EOF'
server:
  local-zone: "shop.test." transparent
  local-data: "api.shop.test. A 10.0.8.51"
EOF
sudo systemctl restart unbound@resolver
sleep 15
