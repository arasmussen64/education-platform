# Two of the three faults fixed (the hysteresis, and web3 kept out in the
# file); the check still asks the database.
on lb sed -i 's|inter 1s fall 1 rise 1|inter 1s fall 3 rise 2|; s|^\(    server web3 .*\)$|\1 disabled|' /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb
sleep 3
