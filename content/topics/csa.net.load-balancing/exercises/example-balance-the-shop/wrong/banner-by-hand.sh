# The walkthrough's saves, but the stock listener is left in mode http and
# the banner is fetched from stock1 directly, past the balancer, and saved.
mkdir -p ~/example
sudo systemctl stop shop-web@web3; sleep 8
journalctl -u haproxy@lb -o cat --since "-1min" | grep 'web3 is DOWN' | tail -n 1 > ~/example/down.txt
sudo systemctl start shop-web@web3
echo 11 > ~/example/hung-seconds.txt
on lb sed -i 's/^    balance roundrobin$/    balance roundrobin\n    option forwardfor/' /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb; sleep 2
on office curl -s http://10.0.9.1/whoami | grep X-Forwarded-For > ~/example/xff.txt
on lb nc -w 2 10.0.1.31 7000 < /dev/null > ~/example/banner.txt
