# Wrong: the blackhole line was taken out. A packet for a store address
# nobody uses follows r2's default route to r1, whose route for the store's
# 10.2.0.0/16 sends it straight back: a loop, until its TTL runs out.
on r2 tee /etc/frr/frr.conf > /dev/null << 'EOF'
frr version 8.4.4
frr defaults traditional
hostname r2
log syslog informational
service integrated-vtysh-config
!
ip route 0.0.0.0/0 10.0.12.1
ip route 10.3.0.0/24 10.0.23.2
ip route 10.3.0.0/24 10.0.12.1 200
!
EOF
sudo systemctl restart frr@r2
