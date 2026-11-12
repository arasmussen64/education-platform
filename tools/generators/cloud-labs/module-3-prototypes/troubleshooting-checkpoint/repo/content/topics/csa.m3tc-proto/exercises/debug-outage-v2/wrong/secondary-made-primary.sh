# Wrong: ns2 is made a primary with a copy of ns1's file.
for i in $(seq 1 30); do on r2 ip route show 10.30.0.0/24 | grep -q tun2 && break; sleep 1; done
sudo cp /etc/netns/ns1/bind/db.shop.test /etc/netns/ns2/bind/db.shop.test
printf 'zone "shop.test" { type primary; file "/etc/bind/db.shop.test"; };
' | sudo tee /etc/netns/ns2/bind/zone.conf > /dev/null
sudo systemctl restart named@ns2
sudo sed -i '/Change 4711/d; /oifname "tun2" tcp dport/d' /etc/netns/r2/nftables.conf && sudo systemctl reload nftables@r2
sudo sed -i 's#ip saddr 10.20.0.0/24 tcp dport 80 accept#ip saddr { 10.10.0.0/24, 10.20.0.0/24 } tcp dport 80 accept#' /etc/netns/app2/nftables.conf && sudo systemctl reload nftables@app2
on resolver unbound-control flush_zone shop.test > /dev/null; on resolver unbound-control flush_infra all > /dev/null; sleep 1
