# Checks every 10 seconds: no flapping, but a hung server keeps its share of
# the traffic for about 3 x (10 + 10) = 60 seconds.
on lb sed -i 's|GET ___|GET /livez|; s|status ___|status 200|; s|inter ___ fall ___ rise ___|inter 10s fall 3 rise 2|' /etc/haproxy/haproxy.cfg
sudo systemctl reset-failed haproxy@lb
sudo systemctl restart haproxy@lb
sleep 5
