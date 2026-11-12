# Wrong: the office's missing names are typed into the office laptop's
# hosts file. curl on that one machine finds them; dig, which asks the
# resolver, and every other machine in the office still don't, and the
# lines go stale the day an address changes.
serial() { on office dig +norecurse +short @"$1" shop.test SOA | awk '{print $3}'; }
on ns1 sed -i 's/198\.51\.100\.24/198.51.100.14/' /etc/bind/named.conf.local
on ns1 rndc reconfig
on ns2 rndc retransfer shop.test
for _ in $(seq 1 20); do [ "$(serial 198.51.100.13)" = "$(serial 198.51.100.14)" ] && break; sleep 1; done
on office tee -a /etc/hosts <<'EOF'
203.0.113.42 mail.shop.test
203.0.113.43 status.shop.test
EOF
on ns1 bash -c 'cd /etc/bind && dnssec-signzone -S -K keys -z -o pay.shop.test -f db.pay.shop.test db.pay.shop.test.unsigned' > /dev/null
on ns1 rndc reload pay.shop.test
sleep 3
