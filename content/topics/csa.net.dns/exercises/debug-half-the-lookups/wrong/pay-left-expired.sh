# Wrong: two of the three faults fixed (ns2's transfers and the office's
# resolver); the payments zone's signatures are left as they were, so
# every resolver that checks signatures still refuses it.
serial() { on office dig +norecurse +short @"$1" shop.test SOA | awk '{print $3}'; }
on ns1 sed -i 's/198\.51\.100\.24/198.51.100.14/' /etc/bind/named.conf.local
on ns1 rndc reconfig
on ns2 rndc retransfer shop.test
for _ in $(seq 1 20); do [ "$(serial 198.51.100.13)" = "$(serial 198.51.100.14)" ] && break; sleep 1; done
on resolver sed -i 's/^  local-zone: "shop.test." static$/  local-zone: "shop.test." transparent/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
sleep 3
