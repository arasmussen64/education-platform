# Wrong: the names and app2 are fixed; r2 still drops web traffic on tun2.
for i in $(seq 1 30); do on r2 ip route show 10.30.0.0/24 | grep -q tun2 && break; sleep 1; done
sudo sed -i "s/2026101501 ; serial/2026111101 ; serial/" /etc/netns/ns1/bind/db.shop.test && sudo systemctl reload named@ns1
for i in $(seq 1 40); do s1=$(on pc dig +short +time=1 +tries=1 @10.20.0.53 shop.test SOA | cut -d" " -f3); s2=$(on pc dig +short +time=1 +tries=1 @10.30.0.200 shop.test SOA | cut -d" " -f3); echo "$s1" | grep -Eq "^[0-9]+$" && [ "$s1" = "$s2" ] && [ "$s1" -gt 2026101501 ] && break; on ns2 rndc refresh shop.test > /dev/null 2>&1; sleep 1; done
sudo sed -i 's#ip saddr 10.20.0.0/24 tcp dport 80 accept#ip saddr { 10.10.0.0/24, 10.20.0.0/24 } tcp dport 80 accept#' /etc/netns/app2/nftables.conf && sudo systemctl reload nftables@app2
on resolver unbound-control flush_zone shop.test > /dev/null; on resolver unbound-control flush_infra all > /dev/null; sleep 1
