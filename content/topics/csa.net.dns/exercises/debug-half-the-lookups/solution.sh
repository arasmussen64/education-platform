# The reference fix: three faults, each found from the evidence.
# serial SERVER: the serial a server gives for shop.test, asked directly.
serial() { on office dig +norecurse +short @"$1" shop.test SOA | awk '{print $3}'; }

# 1. ns2 gives the old address and an older serial than ns1. Its journal
# (journalctl -u named@ns2) says its transfers are REFUSED, and ns1's says
# "zone transfer ... denied": ns1's allow-transfer and also-notify name
# 198.51.100.24, not ns2's 198.51.100.14. rndc reconfig makes ns1 read its
# settings again; ns2 was refused and would only try again after the SOA's
# retry time (600 seconds), so rndc retransfer asks it to fetch the zone
# now.
on ns1 sed -i 's/198\.51\.100\.24/198.51.100.14/' /etc/bind/named.conf.local
on ns1 named-checkconf
on ns1 rndc reconfig
on ns2 rndc retransfer shop.test
until [ -n "$(serial 198.51.100.13)" ] && [ "$(serial 198.51.100.13)" = "$(serial 198.51.100.14)" ]; do sleep 1; done

# 2. In the office, the private zone is static, so the office resolver
# answers every name under shop.test itself, and the names it doesn't hold
# vanish there. transparent answers api from the line below it and
# resolves the rest normally.
on resolver sed -i 's/^  local-zone: "shop.test." static$/  local-zone: "shop.test." transparent/' /etc/unbound/unbound.conf
on resolver unbound-checkconf
sudo systemctl restart unbound@resolver

# 3. A public resolver answers www.pay.shop.test with SERVFAIL and
# "EDE: 7 (Signature Expired)", and the RRSIG dates that ns1 serves ended
# yesterday: the zone is signed by hand and nobody signed it again. Sign it
# again, as its zone file says (signatures for 30 days), and reload it.
on ns1 bash -c 'cd /etc/bind && dnssec-signzone -S -K keys -z -o pay.shop.test -f db.pay.shop.test db.pay.shop.test.unsigned'
on ns1 rndc reload pay.shop.test

# Check through a public resolver that checks signatures: ad, and the
# payments site's address.
until on isp1 dig @198.51.100.21 www.pay.shop.test | grep ' ad' > /dev/null; do sleep 1; done
on office dig +short status.shop.test
