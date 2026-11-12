# Wrong: a more specific route is added to r1's kernel by hand.
sudo sed -i "s/10\.20\.0\.54/10.30.0.200/g" /etc/netns/ns1/bind/zone.conf && sudo systemctl reload named@ns1
# Wait until ns2 has the new copy (right after a boot, BGP may still be coming up).
for i in $(seq 1 40); do s1=$(on pc dig +short +time=1 +tries=1 @10.20.0.53 shop.test SOA | cut -d" " -f3); s2=$(on pc dig +short +time=1 +tries=1 @10.30.0.200 shop.test SOA | cut -d" " -f3); echo "$s1" | grep -Eq "^[0-9]+$" && [ "$s1" = "$s2" ] && break; on ns2 rndc retransfer shop.test 2>/dev/null; sleep 1; done
on r1 ip route add 10.30.0.0/26 via 10.0.12.2
sudo sed -i "s/ct state established accept/ct state established,related accept/" /etc/netns/app2/nftables.conf && sudo systemctl reload nftables@app2
on resolver unbound-control flush_zone shop.test > /dev/null; on resolver unbound-control flush_infra all > /dev/null
