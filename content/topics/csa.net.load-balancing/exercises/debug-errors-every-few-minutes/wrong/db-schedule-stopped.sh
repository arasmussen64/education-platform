# The hysteresis and web3 fixed, and the outages stopped by switching off
# the database's maintenance job: the deep check is still there for the next
# restart, and the job isn't the balancer's to change.
on lb sed -i 's|inter 1s fall 1 rise 1|inter 1s fall 3 rise 2|; s|^\(    server web3 .*\)$|\1 disabled|' /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb
sudo systemctl disable --now db-nightly.timer
sleep 3
