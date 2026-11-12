# Wrong: the office's override is given to the running resolver only, with
# unbound-control, and never written into its /etc/unbound/unbound.conf:
# the next restart of the resolver forgets it.
mkdir -p ~/example
on office dig @198.51.100.11 +norecurse +noall +authority api.shop.test | awk '$4 == "NS" {print $5}' > ~/example/referral.txt
on office dig @198.51.100.13 +norecurse api.shop.test | grep 'flags:' > ~/example/aa.txt
first=$(on office dig +noall +answer api.shop.test | awk '{print $2}')
sleep 2
second=$(on office dig +noall +answer api.shop.test | awk '{print $2}')
echo $((first - second)) > ~/example/countdown.txt
on office dig @198.51.100.13 +norecurse +noall +authority nope.shop.test | awk '$4 == "SOA" {print $2}' > ~/example/negative-ttl.txt
on resolver unbound-control local_zone shop.test transparent
on resolver unbound-control local_data "api.shop.test. A 10.0.8.41"
