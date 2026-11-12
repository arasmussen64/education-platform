# Wrong: the office's names come back by deleting the office's private zone
# altogether, so the office now reaches the API on its public address
# instead of the private one.
serial() { on office dig +norecurse +short @"$1" shop.test SOA | awk '{print $3}'; }
on ns1 sed -i 's/198\.51\.100\.24/198.51.100.14/' /etc/bind/named.conf.local
on ns1 rndc reconfig
on ns2 rndc retransfer shop.test
for _ in $(seq 1 20); do [ "$(serial 198.51.100.13)" = "$(serial 198.51.100.14)" ] && break; sleep 1; done
on resolver sed -i -e '/^  local-zone: "shop.test." static$/d' -e '/^  local-data: "api.shop.test. A 10.0.8.51"$/d' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
on ns1 bash -c 'cd /etc/bind && dnssec-signzone -S -K keys -z -o pay.shop.test -f db.pay.shop.test db.pay.shop.test.unsigned' > /dev/null
on ns1 rndc reload pay.shop.test
sleep 3
