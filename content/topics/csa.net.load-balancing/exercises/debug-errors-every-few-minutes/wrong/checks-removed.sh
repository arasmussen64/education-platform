# No health checks at all (no flapping, and nothing for the database to
# break), and web3 kept out in the file: but a hung server now keeps its
# share of the traffic for ever.
on lb sed -i '/option httpchk/d; /http-check expect/d; s| check cookie| cookie|; s|^\(    server web3 .*\)$|\1 disabled|' /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb
sleep 3
