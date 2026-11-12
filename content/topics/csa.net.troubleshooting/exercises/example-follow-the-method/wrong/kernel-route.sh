# The walkthrough's notes, and a route more specific still typed into r1's
# kernel to win over the stale one: the loads work, the stale route stays in
# FRR, and the kernel route is gone at the next boot.
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
on r1 ip route add 10.30.0.0/26 via 10.0.12.2 dev eth0
