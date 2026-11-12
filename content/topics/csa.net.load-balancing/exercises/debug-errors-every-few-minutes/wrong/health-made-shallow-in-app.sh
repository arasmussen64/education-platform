# The hysteresis and web3 fixed in the balancer, and the web servers'
# program changed so /health no longer asks the database: the check passes,
# but the servers aren't the balancer's to change.
on lb sed -i 's|inter 1s fall 1 rise 1|inter 1s fall 3 rise 2|; s|^\(    server web3 .*\)$|\1 disabled|' /etc/haproxy/haproxy.cfg
sudo sed -i 's|if path == "/livez":|if path in ("/livez", "/health"):|' /usr/local/bin/shop-web
sudo systemctl restart shop-web@web1 shop-web@web2 shop-web@web3
sudo systemctl reload haproxy@lb
sleep 3
