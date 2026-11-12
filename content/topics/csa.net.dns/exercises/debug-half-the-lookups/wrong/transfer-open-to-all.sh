# Wrong: the three faults are fixed, but ns2's transfers are mended by
# letting anyone copy the zone (allow-transfer { any; }) instead of naming
# ns2's address. ns2 is in step again, and so is every stranger who asks
# for the whole zone: a list of every name the shop has.
serial() { on office dig +norecurse +short @"$1" shop.test SOA | awk '{print $3}'; }
on ns1 sed -i 's/allow-transfer { 198\.51\.100\.24; };/allow-transfer { any; };/' /etc/bind/named.conf.local
on ns1 rndc reconfig
on ns2 rndc retransfer shop.test
for _ in $(seq 1 20); do [ "$(serial 198.51.100.13)" = "$(serial 198.51.100.14)" ] && break; sleep 1; done
on resolver sed -i 's/^  local-zone: "shop.test." static$/  local-zone: "shop.test." transparent/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
on ns1 bash -c 'cd /etc/bind && dnssec-signzone -S -K keys -z -o pay.shop.test -f db.pay.shop.test db.pay.shop.test.unsigned' > /dev/null
on ns1 rndc reload pay.shop.test
sleep 3
