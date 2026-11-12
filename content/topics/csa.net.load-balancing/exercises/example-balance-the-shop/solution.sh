netlab show
for ip in 10.0.1.11 10.0.1.12 10.0.1.13; do on lb curl -s http://$ip:8080/; done
on lb cat /etc/haproxy/haproxy.cfg
for i in 1 2 3 4 5 6; do on office curl -s http://10.0.9.1/; done
for i in 1 2 3 4; do on office curl -s http://10.0.9.1/api/whoami | head -n 1; done
echo "show stat" | on lb socat stdio /run/haproxy/admin.sock | awk -F, '$1 == "web" {print $2, $18, $23, $8}'
echo "show servers state web" | on lb socat stdio /run/haproxy/admin.sock
sudo systemctl stop shop-web@web3; sleep 8
mkdir -p ~/example
journalctl -u haproxy@lb -o cat --since "-1min" | grep 'web3 is DOWN' | tail -n 1 | tee ~/example/down.txt
echo "show stat" | on lb socat stdio /run/haproxy/admin.sock | awk -F, '$1 == "web" {print $2, $18, $23, $8}'
for i in 1 2 3 4 5 6; do on office curl -s http://10.0.9.1/; done
sudo systemctl start shop-web@web3; sleep 6
echo "show stat" | on lb socat stdio /run/haproxy/admin.sock | awk -F, '$2 == "web3" {print $2, $18, $23}'
sudo systemctl kill -s STOP shop-web@web2; start=$SECONDS
until echo "show stat" | on lb socat stdio /run/haproxy/admin.sock | grep '^web,web2,' | grep DOWN > /dev/null; do sleep 0.5; done
echo $((SECONDS - start)) | tee ~/example/hung-seconds.txt
journalctl -u haproxy@lb -o cat --since "-1min" | grep 'web2 is DOWN' | tail -n 1
sudo systemctl kill -s CONT shop-web@web2
on office curl -s http://10.0.9.1/whoami
on lb sed -i 's/^    balance roundrobin$/    balance roundrobin\n    option forwardfor/' /etc/haproxy/haproxy.cfg
on lb haproxy -c -f /etc/haproxy/haproxy.cfg && sudo systemctl reload haproxy@lb; sleep 2
on office curl -s http://10.0.9.1/whoami | tee ~/example/whoami.txt
grep X-Forwarded-For ~/example/whoami.txt > ~/example/xff.txt; on office curl -s http://10.0.9.1/api/whoami
on office nc -w 3 10.0.9.1 7000 < /dev/null; echo "nc ended with $?"
on lb sed -i '/^listen stock/,$ s/mode http/mode tcp/' /etc/haproxy/haproxy.cfg
on lb haproxy -c -f /etc/haproxy/haproxy.cfg && sudo systemctl reload haproxy@lb; sleep 2
on office nc -w 3 10.0.9.1 7000 < /dev/null | tee ~/example/banner.txt
rm -f ~/example/jar; for i in 1 2 3 4; do on office curl -s -b ~/example/jar -c ~/example/jar http://10.0.9.1/; done
sticky=$(awk '$6 == "SHOPSRV" {print $7}' ~/example/jar); echo "$sticky"
echo "set server web/$sticky state drain" | on lb socat stdio /run/haproxy/admin.sock
echo "show stat" | on lb socat stdio /run/haproxy/admin.sock | awk -F, '$1 == "web" {print $2, $18}'
for i in 1 2 3 4; do on office curl -s http://10.0.9.1/; done
for i in 1 2; do on office curl -s -b ~/example/jar http://10.0.9.1/; done
echo "set server web/$sticky state ready" | on lb socat stdio /run/haproxy/admin.sock
ls ~/example
