# Wrong: ns2 is taken out of service instead of being mended: it is removed
# from the zone's NS records and stopped. test. still sends resolvers to
# it, and the zone now has one server.
on ns1 sed -i -e '/^@        IN NS    ns2$/d' -e 's/2026111202/2026111203/' /etc/bind/db.shop.test
on ns1 rndc reload shop.test
sudo systemctl disable --now named@ns2
on resolver sed -i 's/^  local-zone: "shop.test." static$/  local-zone: "shop.test." transparent/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
on ns1 bash -c 'cd /etc/bind && dnssec-signzone -S -K keys -z -o pay.shop.test -f db.pay.shop.test db.pay.shop.test.unsigned' > /dev/null
on ns1 rndc reload pay.shop.test
sleep 3
