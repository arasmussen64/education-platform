# The walkthrough's saves, but web3 is never started again after it was
# stopped: a web server is left out of rotation.
mkdir -p ~/example
sudo systemctl stop shop-web@web3; sleep 8
journalctl -u haproxy@lb -o cat --since "-1min" | grep 'web3 is DOWN' | tail -n 1 > ~/example/down.txt
echo 11 > ~/example/hung-seconds.txt
on lb sed -i 's/^    balance roundrobin$/    balance roundrobin\n    option forwardfor/' /etc/haproxy/haproxy.cfg
on lb sed -i '/^listen stock/,$ s/mode http/mode tcp/' /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb; sleep 2
on office curl -s http://10.0.9.1/whoami | grep X-Forwarded-For > ~/example/xff.txt
on office nc -w 2 10.0.9.1 7000 < /dev/null > ~/example/banner.txt
