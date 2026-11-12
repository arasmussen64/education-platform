# Wrong: keepalive is switched on, but the first probe comes after 20 s of
# quiet, and nat has forgotten the connection after 15. Everything else is
# done.
mkdir -p ~/example
# (The reset capture, which takes 20 s of quiet, is left out: it has its own
# wrong fix, and this one fails that check too.)
on app timeout 5 tcpdump -nn -i eth1 tcp port 5432 > ~/example/one-order.txt 2> /dev/null &
sleep 1; (echo 'order 1'; sleep 1) | on app nc -N -w 3 10.0.2.20 5432
wait
echo 'db_keepalive = on' | on app tee -a /etc/shop/api.conf
echo 'db_keepalive_idle = 20' | on app tee -a /etc/shop/api.conf
echo 'db_keepalive_interval = 5' | on app tee -a /etc/shop/api.conf
sudo systemctl restart shop-api@app
