# Wrong: two of the three faults fixed (the office's resolver and the
# payments zone's signatures); ns1 still refuses ns2 the zone, so ns2 keeps
# handing out the API's old address.
on resolver sed -i 's/^  local-zone: "shop.test." static$/  local-zone: "shop.test." transparent/' /etc/unbound/unbound.conf
sudo systemctl restart unbound@resolver
on ns1 bash -c 'cd /etc/bind && dnssec-signzone -S -K keys -z -o pay.shop.test -f db.pay.shop.test db.pay.shop.test.unsigned' > /dev/null
on ns1 rndc reload pay.shop.test
sleep 3
