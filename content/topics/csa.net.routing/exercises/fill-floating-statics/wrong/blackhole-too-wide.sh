# Wrong: the blackhole covers all of 10.0.0.0/8. It stops the loop, but r2
# reaches the office only by its default route, and the /8 is longer than
# the default, so the store's replies to the office die at r2 too.
on r2 tee /etc/frr/frr.conf > /dev/null << 'EOF'
frr version 8.4.4
frr defaults traditional
hostname r2
log syslog informational
service integrated-vtysh-config
!
ip route 0.0.0.0/0 10.0.12.1
ip route 10.0.0.0/8 blackhole
ip route 10.3.0.0/24 10.0.23.2
ip route 10.3.0.0/24 10.0.12.1 200
!
EOF
sudo systemctl restart frr@r2
