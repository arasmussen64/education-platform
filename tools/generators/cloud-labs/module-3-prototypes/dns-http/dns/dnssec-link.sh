#!/bin/bash
# Once, at first boot: put each signed zone's DS record in its parent, and
# the root's into the resolvers' trust anchor. Keys persist under /var/lib/lab.
set -uo pipefail
D=/var/lib/lab/dns
[ -e $D/linked ] && exit 0
waitkey() { for _ in $(seq 1 60); do dig +short +time=1 +tries=1 @$1 $2 DNSKEY | grep -q '^257' && return 0; sleep 1; done; return 1; }
ds() { dig +noall +answer @$1 $2 DNSKEY > /tmp/k.$2 && dnssec-dsfromkey -2 -f /tmp/k.$2 $2; }
bump() { awk '/; serial/ && !d { if (match($0, /[0-9]{10}/)) { s = substr($0, RSTART, RLENGTH) + 1; $0 = substr($0, 1, RSTART-1) s substr($0, RSTART+RLENGTH) }; d=1 } {print}' "$1" > "$1.new" && mv "$1.new" "$1"; chown bind:bind "$1"; }
waitkey 10.0.9.13 shop.test || exit 1
waitkey 10.0.9.12 test || exit 1
waitkey 10.0.9.11 . || exit 1
ds 10.0.9.13 shop.test >> $D/tld/db.test; bump $D/tld/db.test; ip netns exec tld rndc reload test
sleep 2
ds 10.0.9.12 test >> $D/root/db.root; bump $D/root/db.root; ip netns exec root rndc reload .
ds 10.0.9.11 . > $D/root.ds
touch $D/linked
