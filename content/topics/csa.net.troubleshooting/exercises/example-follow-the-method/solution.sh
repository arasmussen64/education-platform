while [ "$(wc -l < /var/log/shop-monitor.log)" -lt 10 ]; do sleep 2; done
mkdir -p ~/example && cp /var/log/shop-monitor.log ~/example/before.log
tail -n 12 ~/example/before.log
echo 'scope = some-loads-slow' >> ~/example/notes.txt
awk '{print $3, ($5 >= 1 ? "slow" : "instant")}' ~/example/before.log | sort | uniq -c
awk '$5 >= 1 {slow++} END {printf "%.0f\n", 100 * slow / NR}' ~/example/before.log
echo "slow_share = $(awk '$5 >= 1 {slow++} END {printf "%.0f\n", 100 * slow / NR}' ~/example/before.log)" >> ~/example/notes.txt
on pc curl -s -m 3 -o /dev/null -w '%{http_code} %{time_total}\n' -H 'Host: www.shop.test' http://10.30.0.11/health
on pc curl -s -m 3 -o /dev/null -w '%{http_code} %{time_total}\n' -H 'Host: www.shop.test' http://10.20.0.11/health
echo 'fails_by_address = 10.30.0.11' >> ~/example/notes.txt
on pc traceroute -n -w 1 -q 1 -m 5 10.30.0.11
on r1 ip route get 10.30.0.11
on r1 ip route get 10.30.0.200
on r1 vtysh -c 'show ip route'
echo 'where = r1' >> ~/example/notes.txt
echo 'cause = stale-more-specific-route' >> ~/example/notes.txt
echo 'evidence = S>* 10.30.0.0/25 [1/0] via 10.0.99.2, old0' >> ~/example/notes.txt
on r1 vtysh -c 'configure terminal' -c 'no ip route 10.30.0.0/25 10.0.99.2' -c 'end' -c 'write memory'
on r1 ip route get 10.30.0.11
for i in $(seq 1 20); do on pc curl -s -o /dev/null -m 3 -w '%{http_code} %{time_total}\n' -H 'Host: www.shop.test' http://10.30.0.11/health; done | awk '{print $1, ($2 < 1 ? "instant" : "slow")}' | sort | uniq -c
for i in $(seq 1 20); do on pc curl -s -o /dev/null -m 3 -w '%{http_code} %{time_total}\n' http://www.shop.test/health; done | awk '{print $1, ($2 < 1 ? "instant" : "slow")}' | sort | uniq -c
echo 'verified = 20/20' >> ~/example/notes.txt
cat ~/example/notes.txt
