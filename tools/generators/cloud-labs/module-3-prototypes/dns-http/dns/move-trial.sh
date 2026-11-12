#!/bin/bash
# Trial of the planned move: the monitor logs what two resolvers and the
# authority say every second; then a right move and a hurried one.
Z=/var/lib/lab/dns/ns1/db.shop.test
setapi() { # ttl address
  sed -i -E "s/^api +[0-9]+ IN A +[0-9.]+/api  $1 IN A     $2/" $Z
  awk '/; serial/ && !d { if (match($0, /[0-9]{10}/)) { s = substr($0, RSTART, RLENGTH) + 1; $0 = substr($0, 1, RSTART-1) s substr($0, RSTART+RLENGTH) }; d=1 } {print}' $Z > $Z.n && mv $Z.n $Z && chown bind:bind $Z
  ip netns exec ns1 rndc reload shop.test >/dev/null
}
monitor() { # log: epoch source answer ttl
  while :; do
    t=$(date +%s.%N | cut -c1-14)
    echo "$t auth $(dig @10.0.9.13 +norecurse +noall +answer api.shop.test A | awk '{print $5, $2}')"
    echo "$t lab $(dig @127.0.0.1 +noall +answer api.shop.test A | awk '{print $5, $2}')"
    echo "$t cafe $(ip netns exec cafe dig @10.0.9.20 +noall +answer api.shop.test A | awk '{print $5, $2}')"
    sleep 1
  done
}
judge() { # change-time newaddr oldaddr newttl
  awk -v tc="$1" -v old="$3" -v nt="$4" '$2 != "auth" && $3 == old && $1 > tc {late = $1 - tc; if (late > max) max = late} END {printf "latest old answer %.1f s after the change (new TTL %d)\n", max, nt}' /tmp/move.log
}
run() { # name wait
  setapi 60 10.0.9.41; sleep 3
  unbound-control -c /etc/lab/resolver.conf flush api.shop.test >/dev/null
  ip netns exec cafe unbound-control -c /etc/lab/cafe.conf flush api.shop.test >/dev/null
  : > /tmp/move.log; monitor >> /tmp/move.log & M=$!
  sleep 20                          # resolvers now hold a 60 s entry
  t_low=$(date +%s); setapi 5 10.0.9.41
  sleep "$2"
  t_change=$(date +%s); setapi 5 10.0.9.51
  sleep 70; kill $M
  echo "$1: waited $2 s after lowering; $(judge $t_change 10.0.9.51 10.0.9.41 5)"
}
run right 62
run hurried 10
