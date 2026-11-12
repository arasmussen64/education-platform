# The check and the hysteresis fixed in the file, but web3 taken out again
# only through the runtime API after the reload: the next restart of the
# balancer forgets it.
on lb sed -i 's|GET /health|GET /livez|; s|inter 1s fall 1 rise 1|inter 1s fall 3 rise 2|' /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy@lb
sleep 2
echo "set server web/web3 state maint" | on lb socat stdio /run/haproxy/admin.sock
sleep 1
