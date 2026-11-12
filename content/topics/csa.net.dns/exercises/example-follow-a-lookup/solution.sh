netlab show
on office cat /etc/resolv.conf
on office dig api.shop.test
on office dig +trace api.shop.test
on office dig @198.51.100.11 +norecurse api.shop.test
mkdir -p ~/example
on office dig @198.51.100.11 +norecurse +noall +authority api.shop.test | awk '$4 == "NS" {print $5}' > ~/example/referral.txt
on office dig @198.51.100.13 +norecurse api.shop.test
on office dig @198.51.100.13 +norecurse api.shop.test | grep 'flags:' > ~/example/aa.txt
on ns1 cat /etc/bind/db.shop.test
on office dig @198.51.100.13 +norecurse +short shop.test SOA
on office dig @198.51.100.14 +norecurse +short shop.test SOA
first=$(on office dig +noall +answer api.shop.test | awk '{print $2}')
sleep 2
second=$(on office dig +noall +answer api.shop.test | awk '{print $2}')
echo $((first - second)) > ~/example/countdown.txt
on office dig nope.shop.test
on office dig @198.51.100.13 +norecurse +noall +authority nope.shop.test | awk '$4 == "SOA" {print $2}' > ~/example/negative-ttl.txt
on office dig +dnssec api.shop.test
on office dig @198.51.100.12 +norecurse +dnssec shop.test DS
on resolver unbound-control local_zone shop.test static
on resolver unbound-control local_data "api.shop.test. A 10.0.8.41"
on office dig +short api.shop.test
on office dig www.shop.test
sudo systemctl restart unbound@resolver
on office dig +short www.shop.test
on resolver tee -a /etc/unbound/unbound.conf <<'EOF'
server:
  local-zone: "shop.test." transparent
  local-data: "api.shop.test. A 10.0.8.41"
EOF
sudo systemctl restart unbound@resolver
on office dig +short api.shop.test
on office dig +short www.shop.test
