# Wrong: ns1's allow-transfer and also-notify are corrected and ns1 reads
# them again, but nothing asks ns2 to fetch the zone: it was refused at boot
# and waits out the SOA's retry time (600 seconds) before it tries again,
# serving its old copy meanwhile.
on ns1 sed -i 's/198\.51\.100\.24/198.51.100.14/' /etc/bind/named.conf.local
on ns1 rndc reconfig
on resolver sed -i 's/^  local-zone: "shop.test." static$/  local-zone: "shop.test." transparent/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
on ns1 bash -c 'cd /etc/bind && dnssec-signzone -S -K keys -z -o pay.shop.test -f db.pay.shop.test db.pay.shop.test.unsigned' > /dev/null
on ns1 rndc reload pay.shop.test
sleep 3
