# The three fixes, each where its fault is. Right after a boot BGP takes a few
# seconds to come up, so wait for both tunnels first.
for i in $(seq 1 30); do on r2 ip route show 10.30.0.0/24 | grep -q tun2 && break; sleep 1; done
# 1. On 3 November www was moved to two servers in ns1's zone file, but the
#    serial wasn't raised, so ns2 was told 'nothing new' and kept October's copy.
sudo sed -i "s/2026101501 ; serial/2026111101 ; serial/" /etc/netns/ns1/bind/db.shop.test && sudo systemctl reload named@ns1
for i in $(seq 1 40); do s1=$(on pc dig +short +time=1 +tries=1 @10.20.0.53 shop.test SOA | cut -d" " -f3); s2=$(on pc dig +short +time=1 +tries=1 @10.30.0.200 shop.test SOA | cut -d" " -f3); echo "$s1" | grep -Eq "^[0-9]+$" && [ "$s1" = "$s2" ] && [ "$s1" -gt 2026101501 ] && break; on ns2 rndc refresh shop.test > /dev/null 2>&1; sleep 1; done
# 2. r2's firewall still keeps web traffic off tun2 (change 4711), so every
#    connection the tunnels' sharing sends over tun2 is dropped.
sudo sed -i '/Change 4711/d; /oifname "tun2" tcp dport/d' /etc/netns/r2/nftables.conf && sudo systemctl reload nftables@r2
# 3. app2 lets in web traffic from the data centre only, where its old load
#    balancer was; the office's connections were dropped.
sudo sed -i 's#ip saddr 10.20.0.0/24 tcp dport 80 accept#ip saddr { 10.10.0.0/24, 10.20.0.0/24 } tcp dport 80 accept#' /etc/netns/app2/nftables.conf && sudo systemctl reload nftables@app2
# The resolver may hold an old answer for up to 30 seconds; empty it.
on resolver unbound-control flush_zone shop.test > /dev/null; on resolver unbound-control flush_infra all > /dev/null; sleep 1
