# Worked out with a fixed-clock balancer's sum, fall x inter + timeout =
# 2 x 4 + 4 = 12 seconds, which looks within the 15. But HAProxy waits inter
# after each check ends, so a server that hangs just after a good check is
# out only after 2 x (4 + 4) = 16 seconds.
on lb sed -i 's|GET ___|GET /livez|; s|status ___|status 200|; s|inter ___ fall ___ rise ___|inter 4s fall 2 rise 2|' /etc/haproxy/haproxy.cfg
sudo systemctl reset-failed haproxy@lb
sudo systemctl restart haproxy@lb
sleep 5
