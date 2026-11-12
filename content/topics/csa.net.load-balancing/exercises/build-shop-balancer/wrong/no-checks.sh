# No health checks at all, to stop any server flapping: a hung server keeps
# its share of the traffic for ever.
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
    default-server inter 1s fall 3 rise 2
    server web1 10.0.1.11:8080 cookie web1
    server web2 10.0.1.12:8080 cookie web2
    server web3 10.0.1.13:8080 cookie web3

backend api
    balance roundrobin
    default-server inter 1s fall 3 rise 2
    server api1 10.0.1.21:8081
    server api2 10.0.1.22:8081

listen stock
    bind 10.0.9.1:7000
    mode tcp
    option tcplog
    balance roundrobin
    server stock1 10.0.1.31:7000
    server stock2 10.0.1.32:7000
EOF
sudo systemctl reset-failed haproxy@lb
sudo systemctl restart haproxy@lb
sleep 4
