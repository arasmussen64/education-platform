# The check asks /health, which needs the database too: when the database
# restarts, every web server fails its checks at once.
on lb sed -i 's|GET ___|GET /health|; s|status ___|status 200|; s|inter ___ fall ___ rise ___|inter 2s fall 3 rise 2|' /etc/haproxy/haproxy.cfg
sudo systemctl reset-failed haproxy@lb
sudo systemctl restart haproxy@lb
sleep 5
