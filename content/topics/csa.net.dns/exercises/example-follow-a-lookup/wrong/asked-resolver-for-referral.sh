# Wrong: the "one referral by hand" step asks the office's resolver instead
# of the root (no @198.51.100.11), and saves what it got: the address
# itself, not the name of the server the root refers the question to.
mkdir -p ~/example
on office dig +short api.shop.test > ~/example/referral.txt
on office dig @198.51.100.13 +norecurse api.shop.test | grep 'flags:' > ~/example/aa.txt
first=$(on office dig +noall +answer api.shop.test | awk '{print $2}')
sleep 2
second=$(on office dig +noall +answer api.shop.test | awk '{print $2}')
echo $((first - second)) > ~/example/countdown.txt
on office dig @198.51.100.13 +norecurse +noall +authority nope.shop.test | awk '$4 == "SOA" {print $2}' > ~/example/negative-ttl.txt
on resolver tee -a /etc/unbound/unbound.conf <<'EOF'
server:
  local-zone: "shop.test." transparent
  local-data: "api.shop.test. A 10.0.8.41"
EOF
sudo systemctl restart unbound@resolver
