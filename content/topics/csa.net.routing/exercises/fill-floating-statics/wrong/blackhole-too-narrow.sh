# Wrong: the blackhole covers only the lower half of the store's /16,
# 10.2.0.0/17 (10.2.0.0 to 10.2.127.255). Unused addresses in the upper
# half, 10.2.200.9 among them, still follow r2's default route to r1,
# which sends them straight back: a loop.
on r2 tee /etc/frr/frr.conf > /dev/null << 'EOF'
frr version 8.4.4
frr defaults traditional
hostname r2
log syslog informational
service integrated-vtysh-config
!
ip route 0.0.0.0/0 10.0.12.1
ip route 10.2.0.0/17 blackhole
ip route 10.3.0.0/24 10.0.23.2
ip route 10.3.0.0/24 10.0.12.1 200
!
EOF
sudo systemctl restart frr@r2
