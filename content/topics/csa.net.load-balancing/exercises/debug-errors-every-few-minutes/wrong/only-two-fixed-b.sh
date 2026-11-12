# Two of the three faults fixed (the check asks /livez, and web3 is kept
# out in the file); one failed check still takes a server out.
on lb sed -i 's|GET /health|GET /livez|; s|^\(    server web3 .*\)$|\1 disabled|' /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb
sleep 3
