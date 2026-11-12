# The reference balancer, but a recovered server is put back after a single
# good check (rise 1): one good moment of a server that keeps failing is
# enough to send it visitors again.
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
    default-server inter 1s fall 3 rise 1
    server web1 10.0.1.11:8080 check cookie web1
    server web2 10.0.1.12:8080 check cookie web2
    server web3 10.0.1.13:8080 check cookie web3

backend api
    balance roundrobin
    option httpchk GET /livez
    http-check expect status 200
    default-server inter 1s fall 3 rise 1
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
sudo systemctl reset-failed haproxy@lb
sudo systemctl restart haproxy@lb
sleep 4
