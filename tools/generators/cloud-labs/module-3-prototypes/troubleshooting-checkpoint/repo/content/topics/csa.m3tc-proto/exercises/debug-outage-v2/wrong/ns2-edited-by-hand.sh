# Wrong: ns1's file is copied over ns2's copy by hand; the serial is still October's.
for i in $(seq 1 30); do on r2 ip route show 10.30.0.0/24 | grep -q tun2 && break; sleep 1; done
sudo install -o bind -g bind -m 644 /etc/netns/ns1/bind/db.shop.test /var/lib/netlab/machines/ns2/var/cache/bind/shop.test.db && sudo systemctl restart named@ns2
sudo sed -i '/Change 4711/d; /oifname "tun2" tcp dport/d' /etc/netns/r2/nftables.conf && sudo systemctl reload nftables@r2
sudo sed -i 's#ip saddr 10.20.0.0/24 tcp dport 80 accept#ip saddr { 10.10.0.0/24, 10.20.0.0/24 } tcp dport 80 accept#' /etc/netns/app2/nftables.conf && sudo systemctl reload nftables@app2
on resolver unbound-control flush_zone shop.test > /dev/null; on resolver unbound-control flush_infra all > /dev/null; sleep 1
