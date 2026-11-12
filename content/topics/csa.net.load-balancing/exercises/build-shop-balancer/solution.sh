# The reference balancer. on lb tee FILE <<'EOF' writes every line up to EOF
# into lb's file (the quotes round 'EOF' keep the shell from changing
# anything inside); a learner writes the sections with nano.
#
# One frontend for the web traffic, routing /api/ by its path (layer 7) and
# adding X-Forwarded-For to every request; the web backend sticky by an
# inserted cookie, since the whole office comes from one address; the API
# backend; and the stock service as a layer 4 listener, because its server
# speaks first. Every web and API server is checked with /livez, which
# tests the server and not the database they share, every second, out
# after 3 failures in a row and back after 2 good checks: a hung server is
# out after about 3 x (1 + 1) = 6 seconds, well within the 15.
on lb tee /etc/haproxy/haproxy.cfg > /dev/null <<'EOF'
global
    log stdout format raw local0
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s

defaults
    mode http
    log global
    option httplog
    timeout connect 2s
    timeout client 30s
    timeout server 30s

frontend shop
    bind 10.0.9.1:80
    option forwardfor
    use_backend api if { path_beg /api/ }
    default_backend web

backend web
    balance roundrobin
    cookie SHOPSRV insert indirect nocache
    option httpchk GET /livez
    http-check expect status 200
    default-server inter 1s fall 3 rise 2
    server web1 10.0.1.11:8080 check cookie web1
    server web2 10.0.1.12:8080 check cookie web2
    server web3 10.0.1.13:8080 check cookie web3

backend api
    balance roundrobin
    option httpchk GET /livez
    http-check expect status 200
    default-server inter 1s fall 3 rise 2
    server api1 10.0.1.21:8081 check
    server api2 10.0.1.22:8081 check

listen stock
    bind 10.0.9.1:7000
    mode tcp
    option tcplog
    balance roundrobin
    server stock1 10.0.1.31:7000 check
    server stock2 10.0.1.32:7000 check
EOF
on lb haproxy -c -f /etc/haproxy/haproxy.cfg
# HAProxy failed at boot with no sections to run, so it is started, not
# reloaded (reset-failed clears systemd's refusal to start a unit that
# failed several times a moment ago); it is already enabled at boot.
sudo systemctl reset-failed haproxy@lb
sudo systemctl restart haproxy@lb
sleep 4
for i in 1 2 3; do on office curl -s http://10.0.9.1/; done
on office curl -s http://10.0.9.1/api/whoami
on office nc -w 2 10.0.9.1 7000 < /dev/null
