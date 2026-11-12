# Wrong: r2 is right, but r1 was changed too, and r1 isn't the learner's
# to change: its route for the store was narrowed to the one /24 the store
# uses, and saved.
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
ip route 10.3.0.0/24 10.0.12.1 200
!
EOF
sudo systemctl restart frr@r2
on r1 vtysh -c 'configure terminal' -c 'no ip route 10.2.0.0/16 10.0.12.2' -c 'no ip route 10.2.0.0/16 10.0.13.2 200' \
  -c 'ip route 10.2.0.0/24 10.0.12.2' -c 'ip route 10.2.0.0/24 10.0.13.2 200' -c 'end' -c 'write memory' > /dev/null
