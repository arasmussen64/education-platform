# HAProxy started with a first try (fall 1 rise 1); the file was then put
# right and never reloaded, so the balancer still runs the first try.
on lb sed -i 's|GET ___|GET /livez|; s|status ___|status 200|; s|inter ___ fall ___ rise ___|inter 2s fall 1 rise 1|' /etc/haproxy/haproxy.cfg
sudo systemctl reset-failed haproxy@lb
sudo systemctl restart haproxy@lb
sleep 2
on lb sed -i 's|fall 1 rise 1|fall 3 rise 2|' /etc/haproxy/haproxy.cfg
