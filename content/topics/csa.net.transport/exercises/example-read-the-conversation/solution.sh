netlab show
mkdir -p ~/example
on app timeout 5 tcpdump -nn -i eth1 tcp port 5432 > ~/example/one-order.txt &
sleep 1; (echo 'order 1'; sleep 1) | on app nc -N -w 3 10.0.2.20 5432
wait
cat ~/example/one-order.txt
on app ss -tno state time-wait '( dport = :5432 )'
on app curl -s localhost:8080/order
on app curl -s localhost:8080/order
on app ss -tno '( dport = :5432 )'
on nat sysctl net.netfilter.nf_conntrack_tcp_timeout_established
on nat conntrack -L -p tcp --dport 5432
sleep 20
on app curl -s localhost:8080/order
journalctl -u shop-api@app -n 3
on app timeout 25 tcpdump -nn -v -i eth1 'tcp port 5432 and tcp[tcpflags] & (tcp-rst|tcp-syn) != 0' > ~/example/reset.txt &
sleep 1; on app curl -s localhost:8080/order
sleep 20; on app curl -s localhost:8080/order
wait
cat ~/example/reset.txt
echo 'db_keepalive = on' | on app tee -a /etc/shop/api.conf
echo 'db_keepalive_idle = 5' | on app tee -a /etc/shop/api.conf
echo 'db_keepalive_interval = 5' | on app tee -a /etc/shop/api.conf
sudo systemctl restart shop-api@app
on app curl -s localhost:8080/order
on app ss -tno '( dport = :5432 )'
on nat timeout 20 tcpdump -nn -i outside tcp port 5432 > ~/example/quiet.txt &
sleep 21; on app curl -s localhost:8080/order
cat ~/example/quiet.txt
on app iperf3 -c 10.0.6.20 -t 5
on app iperf3 -c 10.0.6.20 -t 5 > /dev/null & sleep 3; on app ss -tni dst 10.0.6.20; wait
on dr sysctl -w net.ipv4.tcp_window_scaling=0
on app iperf3 -c 10.0.6.20 -t 5
on dr sysctl -w net.ipv4.tcp_window_scaling=1
