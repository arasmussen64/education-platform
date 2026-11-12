# Wrong: the reset is captured without -v, so the capture shows no TTLs and
# can't tell the database's packets from nat's. Everything else is done.
mkdir -p ~/example
on app timeout 5 tcpdump -nn -i eth1 tcp port 5432 > ~/example/one-order.txt 2> /dev/null &
sleep 1; (echo 'order 1'; sleep 1) | on app nc -N -w 3 10.0.2.20 5432
wait
on app timeout 24 tcpdump -nn -i eth1 'tcp port 5432 and tcp[tcpflags] & (tcp-rst|tcp-syn) != 0' > ~/example/reset.txt 2> /dev/null &
sleep 1; on app curl -s localhost:8080/order
sleep 20; on app curl -s localhost:8080/order
wait
echo 'db_keepalive = on' | on app tee -a /etc/shop/api.conf
echo 'db_keepalive_idle = 5' | on app tee -a /etc/shop/api.conf
echo 'db_keepalive_interval = 5' | on app tee -a /etc/shop/api.conf
sudo systemctl restart shop-api@app
