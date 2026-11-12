# Wrong: the resolver no longer asks ns2; ns2 still serves its old copy.
for i in $(seq 1 30); do on r2 ip route show 10.30.0.0/24 | grep -q tun2 && break; sleep 1; done
sudo sed -i '/stub-addr: 10.30.0.200/d' /etc/netns/resolver/unbound/unbound.conf && sudo systemctl restart unbound@resolver
sudo sed -i '/Change 4711/d; /oifname "tun2" tcp dport/d' /etc/netns/r2/nftables.conf && sudo systemctl reload nftables@r2
sudo sed -i 's#ip saddr 10.20.0.0/24 tcp dport 80 accept#ip saddr { 10.10.0.0/24, 10.20.0.0/24 } tcp dport 80 accept#' /etc/netns/app2/nftables.conf && sudo systemctl reload nftables@app2
sleep 2
