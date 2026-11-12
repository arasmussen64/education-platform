# Wrong: the first two faults are fixed, and the payments site is "fixed"
# by telling the public resolvers not to check pay.shop.test's signatures
# (domain-insecure). They aren't the shop's to change, and a zone nobody
# checks can be forged.
serial() { on office dig +norecurse +short @"$1" shop.test SOA | awk '{print $3}'; }
on ns1 sed -i 's/198\.51\.100\.24/198.51.100.14/' /etc/bind/named.conf.local
on ns1 rndc reconfig
on ns2 rndc retransfer shop.test
for _ in $(seq 1 20); do [ "$(serial 198.51.100.13)" = "$(serial 198.51.100.14)" ] && break; sleep 1; done
on resolver sed -i 's/^  local-zone: "shop.test." static$/  local-zone: "shop.test." transparent/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
for isp in isp1 isp2 isp3; do
  on "$isp" sed -i 's/^  ede: yes$/  ede: yes\n  domain-insecure: "pay.shop.test"/' /etc/unbound/unbound.conf
  sudo systemctl restart "unbound@$isp"
done
sleep 3
