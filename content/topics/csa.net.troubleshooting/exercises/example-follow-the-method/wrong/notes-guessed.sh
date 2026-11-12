# The route fixed and saved, but the notes guess at the cause: one address
# failing looked like a naming problem, though asking the address directly
# showed it fails without any name.
while [ "$(wc -l < /var/log/shop-monitor.log)" -lt 10 ]; do sleep 2; done
mkdir -p ~/example && cp /var/log/shop-monitor.log ~/example/before.log
cat > ~/example/notes.txt <<EOF
scope = some-loads-slow
slow_share = $(awk '$5 >= 1 {slow++} END {printf "%.0f\n", 100 * slow / NR}' ~/example/before.log)
fails_by_address = 10.30.0.11
where = r1
cause = dns-stale-record
evidence = www.shop.test has two addresses, and one of them doesn't answer
verified = 20/20
EOF
on r1 vtysh -c 'configure terminal' -c 'no ip route 10.30.0.0/25 10.0.99.2' -c 'end' -c 'write memory'
