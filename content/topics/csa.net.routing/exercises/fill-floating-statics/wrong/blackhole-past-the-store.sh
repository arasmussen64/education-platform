# Wrong: the blackhole is one bit too wide, 10.2.0.0/15, which holds
# 10.3.0.0/16 as well as the store's 10.2.0.0/16. The office still works
# (it isn't inside), and the data centre's /24 has longer routes, but
# every other 10.3 address, which isn't the store's, now dies at r2
# instead of following r2's default route.
on r2 tee /etc/frr/frr.conf > /dev/null << 'EOF'
frr version 8.4.4
frr defaults traditional
hostname r2
log syslog informational
service integrated-vtysh-config
!
ip route 0.0.0.0/0 10.0.12.1
ip route 10.2.0.0/15 blackhole
ip route 10.3.0.0/24 10.0.23.2
ip route 10.3.0.0/24 10.0.12.1 200
!
EOF
sudo systemctl restart frr@r2
