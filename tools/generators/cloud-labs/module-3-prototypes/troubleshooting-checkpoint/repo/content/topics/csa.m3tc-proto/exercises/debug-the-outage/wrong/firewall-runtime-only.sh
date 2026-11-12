# Wrong: the rule is added to app2's running firewall, not to its file.
sudo sed -i "s/10\.20\.0\.54/10.30.0.200/g" /etc/netns/ns1/bind/zone.conf && sudo systemctl reload named@ns1
# Wait until ns2 has the new copy (right after a boot, BGP may still be coming up).
for i in $(seq 1 40); do s1=$(on pc dig +short +time=1 +tries=1 @10.20.0.53 shop.test SOA | cut -d" " -f3); s2=$(on pc dig +short +time=1 +tries=1 @10.30.0.200 shop.test SOA | cut -d" " -f3); echo "$s1" | grep -Eq "^[0-9]+$" && [ "$s1" = "$s2" ] && break; on ns2 rndc retransfer shop.test 2>/dev/null; sleep 1; done
on r1 vtysh -c 'conf t' -c 'no ip route 10.30.0.0/25 10.0.99.2' -c 'end' -c 'write memory' > /dev/null
on app2 nft insert rule inet filter input ct state related accept
on resolver unbound-control flush_zone shop.test > /dev/null; on resolver unbound-control flush_infra all > /dev/null
