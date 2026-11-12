# The three fixes, each where its fault is.
# 1. ns2 moved to the cloud (10.30.0.200), but ns1 still lets only its old
#    address copy the zone, so ns2 kept serving October's copy.
sudo sed -i "s/10\.20\.0\.54/10.30.0.200/g" /etc/netns/ns1/bind/zone.conf && sudo systemctl reload named@ns1
# Wait until ns2 has the new copy (right after a boot, BGP may still be coming up).
for i in $(seq 1 40); do s1=$(on pc dig +short +time=1 +tries=1 @10.20.0.53 shop.test SOA | cut -d" " -f3); s2=$(on pc dig +short +time=1 +tries=1 @10.30.0.200 shop.test SOA | cut -d" " -f3); echo "$s1" | grep -Eq "^[0-9]+$" && [ "$s1" = "$s2" ] && break; on ns2 rndc retransfer shop.test 2>/dev/null; sleep 1; done
# 2. r1 still has a fixed route for half the cloud's network through the old
#    VPN appliance, which no longer forwards anything; being more specific
#    than BGP's /24, it wins.
on r1 vtysh -c 'conf t' -c 'no ip route 10.30.0.0/25 10.0.99.2' -c 'end' -c 'write memory' > /dev/null
# 3. app2's firewall drops the ICMP errors that belong to its connections
#    (no "related"), so it never hears that its packets are too big for the
#    tunnel.
sudo sed -i "s/ct state established accept/ct state established,related accept/" /etc/netns/app2/nftables.conf && sudo systemctl reload nftables@app2
# The resolver may hold the old answer for up to 30 seconds; empty it.
on resolver unbound-control flush_zone shop.test > /dev/null; on resolver unbound-control flush_infra all > /dev/null
sleep 2
