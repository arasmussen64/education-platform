# Wrong: the file was rewritten rather than filled in. The default route
# became a route for the office alone, and the blackhole line went. With
# no default route, a store address nobody uses has no route at r2 and
# dies there without a blackhole, but r2 has lost its way to everything
# beyond the office, and the line the gap asked for was never written.
on r2 tee /etc/frr/frr.conf > /dev/null << 'EOF'
frr version 8.4.4
frr defaults traditional
hostname r2
log syslog informational
service integrated-vtysh-config
!
ip route 10.1.0.0/24 10.0.12.1
ip route 10.3.0.0/24 10.0.23.2
ip route 10.3.0.0/24 10.0.12.1 200
!
EOF
sudo systemctl restart frr@r2
