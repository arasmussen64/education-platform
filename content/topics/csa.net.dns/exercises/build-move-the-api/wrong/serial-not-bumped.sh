# Wrong: api's line is edited (the new address, with the move's TTL) but
# the serial is left as it was. ns1 refuses to load the edit ("not loaded
# due to errors" in its journal, though rndc says "zone reload queued"),
# so nothing ever changes for anyone.
on ns1 sed -i -e 's/^api .*/api    5 IN A     203.0.113.51/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
on resolver tee -a /etc/unbound/unbound.conf <<'EOF'
server:
  local-zone: "shop.test." transparent
  local-data: "api.shop.test. A 10.0.8.51"
EOF
sudo systemctl restart unbound@resolver
sleep 12
