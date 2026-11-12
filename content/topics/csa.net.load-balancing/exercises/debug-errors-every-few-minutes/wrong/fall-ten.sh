# The check asks /livez and web3 is kept out in the file, but the flapping
# is stopped with ten failures to go down: a hung server keeps its share for
# about 10 x (1 + 1) = 20 seconds.
on lb sed -i 's|GET /health|GET /livez|; s|inter 1s fall 1 rise 1|inter 1s fall 10 rise 2|; s|^\(    server web3 .*\)$|\1 disabled|' /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb
sleep 3
