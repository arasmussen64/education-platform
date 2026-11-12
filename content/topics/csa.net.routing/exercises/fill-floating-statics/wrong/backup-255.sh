# Wrong: the backup has distance 255, "the least preferred". FRR never
# installs a route at 255, so when the r2-r3 cable goes, the data centre
# has no route at all.
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
ip route 10.3.0.0/24 10.0.12.1 255
!
EOF
sudo systemctl restart frr@r2
