# Wrong: the three faults are fixed, and the office's resolver is also told
# to stop refusing bad signatures (val-permissive-mode), "so nothing in the
# office fails like that again". It now hands forged answers to the office
# as readily as real ones.
serial() { on office dig +norecurse +short @"$1" shop.test SOA | awk '{print $3}'; }
on ns1 sed -i 's/198\.51\.100\.24/198.51.100.14/' /etc/bind/named.conf.local
on ns1 rndc reconfig
on ns2 rndc retransfer shop.test
for _ in $(seq 1 20); do [ "$(serial 198.51.100.13)" = "$(serial 198.51.100.14)" ] && break; sleep 1; done
on resolver sed -i -e 's/^  local-zone: "shop.test." static$/  local-zone: "shop.test." transparent/' -e 's/^  ede: yes$/  ede: yes\n  val-permissive-mode: yes/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
on ns1 bash -c 'cd /etc/bind && dnssec-signzone -S -K keys -z -o pay.shop.test -f db.pay.shop.test db.pay.shop.test.unsigned' > /dev/null
on ns1 rndc reload pay.shop.test
sleep 3
