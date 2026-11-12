# The walkthrough's notes, and the stale route removed from FRR's running
# configuration only: write memory is left out, so the next boot loads the
# route again from /etc/frr/frr.conf.
while [ "$(wc -l < /var/log/shop-monitor.log)" -lt 10 ]; do sleep 2; done
mkdir -p ~/example && cp /var/log/shop-monitor.log ~/example/before.log
cat > ~/example/notes.txt <<EOF
scope = some-loads-slow
slow_share = $(awk '$5 >= 1 {slow++} END {printf "%.0f\n", 100 * slow / NR}' ~/example/before.log)
fails_by_address = 10.30.0.11
where = r1
cause = stale-more-specific-route
evidence = S>* 10.30.0.0/25 [1/0] via 10.0.99.2, old0
verified = 20/20
EOF
on r1 vtysh -c 'configure terminal' -c 'no ip route 10.30.0.0/25 10.0.99.2' -c 'end'
