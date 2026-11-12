# The reference: r2's file with its three gaps filled, then FRR on r2
# restarted so that it loads the file. "on r2 tee FILE <<'EOF'" writes the
# lines up to EOF into the file on r2, as root there; in the lab, nano does
# the same job by hand.
#   - the data centre's network, 10.3.0.0/24, over r2's own cable to r3
#     (r3's end of it is 10.0.23.2);
#   - the same network through r1, at distance 200, a floating static
#     route that FRR installs only when the first one is gone;
#   - the store's whole 10.2.0.0/16 as a blackhole: the store's own
#     10.2.0.0/24 is connected, a longer prefix, so it still wins, and every
#     other store address dies here instead of following the default route
#     back to r1, which would send it straight back.
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
on r2 vtysh -c 'show ip route'
