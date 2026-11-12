# Wrong: ns2 is made a primary with a copy of ns1's file.
sudo cp /etc/netns/ns1/bind/db.shop.test /etc/netns/ns2/bind/db.shop.test
printf 'zone "shop.test" { type primary; file "/etc/bind/db.shop.test"; };\n' | sudo tee /etc/netns/ns2/bind/zone.conf > /dev/null
sudo systemctl restart named@ns2
on r1 vtysh -c 'conf t' -c 'no ip route 10.30.0.0/25 10.0.99.2' -c 'end' -c 'write memory' > /dev/null
sudo sed -i "s/ct state established accept/ct state established,related accept/" /etc/netns/app2/nftables.conf && sudo systemctl reload nftables@app2
on resolver unbound-control flush_zone shop.test > /dev/null; on resolver unbound-control flush_infra all > /dev/null
