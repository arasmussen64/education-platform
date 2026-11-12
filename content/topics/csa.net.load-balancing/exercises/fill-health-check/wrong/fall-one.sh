# Out after one failed check and back after one good one: no hysteresis, so
# a server that fails a check now and then flaps in and out.
on lb sed -i 's|GET ___|GET /livez|; s|status ___|status 200|; s|inter ___ fall ___ rise ___|inter 2s fall 1 rise 1|' /etc/haproxy/haproxy.cfg
sudo systemctl reset-failed haproxy@lb
sudo systemctl restart haproxy@lb
sleep 5
