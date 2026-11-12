# Wrong: the conversation's capture and keepalive are done, but dr's window
# scaling, switched off for one test, is never switched back on.
mkdir -p ~/example
# (The reset capture, which takes 20 s of quiet, is left out: it has its own
# wrong fix, and this one fails that check too.)
on app timeout 5 tcpdump -nn -i eth1 tcp port 5432 > ~/example/one-order.txt 2> /dev/null &
sleep 1; (echo 'order 1'; sleep 1) | on app nc -N -w 3 10.0.2.20 5432
wait
echo 'db_keepalive = on' | on app tee -a /etc/shop/api.conf
echo 'db_keepalive_idle = 5' | on app tee -a /etc/shop/api.conf
echo 'db_keepalive_interval = 5' | on app tee -a /etc/shop/api.conf
sudo systemctl restart shop-api@app
on dr sysctl -w net.ipv4.tcp_window_scaling=0
