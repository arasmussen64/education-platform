# Wrong: the resolver no longer asks ns2; ns2 still serves its old copy.
sudo sed -i '/stub-addr: 10.30.0.200/d' /etc/netns/resolver/unbound/unbound.conf && sudo systemctl restart unbound@resolver
on r1 vtysh -c 'conf t' -c 'no ip route 10.30.0.0/25 10.0.99.2' -c 'end' -c 'write memory' > /dev/null
sudo sed -i "s/ct state established accept/ct state established,related accept/" /etc/netns/app2/nftables.conf && sudo systemctl reload nftables@app2
sleep 2
