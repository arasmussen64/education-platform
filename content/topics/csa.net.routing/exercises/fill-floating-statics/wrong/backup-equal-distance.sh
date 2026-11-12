# Wrong: the backup through r1 has distance 1, the same as the direct
# route, so it isn't a backup: FRR installs both and the kernel shares the
# data centre's traffic between them (ECMP), half of it the long way round.
on r2 tee /etc/frr/frr.conf > /dev/null << 'EOF'
frr version 8.4.4
frr defaults traditional
hostname r2
log syslog informational
service integrated-vtysh-config
!
ip route 0.0.0.0/0 10.0.12.1
ip route 10.2.0.0/16 blackhole
ip route 10.3.0.0/24 10.0.23.2
ip route 10.3.0.0/24 10.0.12.1 1
!
EOF
sudo systemctl restart frr@r2
