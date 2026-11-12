# Wrong: the first two faults are fixed, and the payments site is made to
# resolve by taking its DS record out of shop.test, so resolvers no longer
# expect it to be signed. It resolves, unsigned: anyone who can forge an
# answer can now send customers' payments elsewhere.
serial() { on office dig +norecurse +short @"$1" shop.test SOA | awk '{print $3}'; }
on ns1 sed -i 's/198\.51\.100\.24/198.51.100.14/' /etc/bind/named.conf.local
on ns1 rndc reconfig
on ns1 sed -i -e '/^pay\.shop\.test\. IN DS /d' -e 's/2026111202/2026111203/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
on ns2 rndc retransfer shop.test
for _ in $(seq 1 20); do [ "$(serial 198.51.100.13)" = "$(serial 198.51.100.14)" ] && break; sleep 1; done
on resolver sed -i 's/^  local-zone: "shop.test." static$/  local-zone: "shop.test." transparent/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
sleep 3
