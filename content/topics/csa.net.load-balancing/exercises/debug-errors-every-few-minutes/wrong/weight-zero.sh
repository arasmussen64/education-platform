# The check and the hysteresis fixed, and web3 given weight 0 in the file:
# new visitors never reach it, but a visitor whose cookie names web3 still
# does, and gets its broken pages.
on lb sed -i 's|GET /health|GET /livez|; s|inter 1s fall 1 rise 1|inter 1s fall 3 rise 2|; s|^\(    server web3 .*\)$|\1 weight 0|' /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb
sleep 3
