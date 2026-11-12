#!/bin/bash
# Check: an order after a quiet spell longer than the gateway's idle timeout
# succeeds on the SAME connection, and during the quiet spell only empty
# packets (keepalive probes) crossed the gateway. Prints "kept alive" or why not.
quiet=${1:-38}
first=$(curl -s -m 8 localhost:8080/order)
case "$first" in *'"ok": true'*) ;; *) echo "the first order failed: $first"; exit 0 ;; esac
port1=$(echo "$first" | sed -n 's/.*"port": \([0-9]*\).*/\1/p')
cap=$(mktemp)
ip netns exec nat timeout $((quiet - 1)) tcpdump -nn -l -i out0 "tcp port 5432" > "$cap" 2>/dev/null &
sleep "$quiet"
second=$(curl -s -m 8 localhost:8080/order)
wait
port2=$(echo "$second" | sed -n 's/.*"port": \([0-9]*\).*/\1/p')
probes=$(grep -c 'length 0' "$cap")
data=$(grep -v 'length 0' "$cap" | grep -c 'length')
rm -f "$cap"
case "$second" in *'"ok": true'*) ;; *) echo "the order after ${quiet}s of quiet failed: $second"; exit 0 ;; esac
[ "$port1" = "$port2" ] || { echo "the order after the quiet spell used a new connection (port $port1, then $port2)"; exit 0; }
[ "$probes" -ge 2 ] || { echo "no keepalive probes crossed the gateway during the quiet spell"; exit 0; }
[ "$data" -eq 0 ] || { echo "orders or other data crossed the gateway during the quiet spell ($data packets)"; exit 0; }
echo "kept alive"
