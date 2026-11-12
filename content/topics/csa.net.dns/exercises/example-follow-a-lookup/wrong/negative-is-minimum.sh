# Wrong: the negative TTL is taken to be the SOA's last number, MINIMUM
# (900), but a "no such name" is kept for the smaller of that and the SOA
# record's own TTL: 300 here.
mkdir -p ~/example
on office dig @198.51.100.11 +norecurse +noall +authority api.shop.test | awk '$4 == "NS" {print $5}' > ~/example/referral.txt
on office dig @198.51.100.13 +norecurse api.shop.test | grep 'flags:' > ~/example/aa.txt
first=$(on office dig +noall +answer api.shop.test | awk '{print $2}')
sleep 2
second=$(on office dig +noall +answer api.shop.test | awk '{print $2}')
echo $((first - second)) > ~/example/countdown.txt
on office dig @198.51.100.13 +norecurse +short shop.test SOA | awk '{print $7}' > ~/example/negative-ttl.txt
on resolver tee -a /etc/unbound/unbound.conf <<'EOF'
server:
  local-zone: "shop.test." transparent
  local-data: "api.shop.test. A 10.0.8.41"
EOF
sudo systemctl restart unbound@resolver
