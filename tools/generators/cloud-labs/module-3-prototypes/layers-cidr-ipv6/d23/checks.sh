#!/bin/bash
# Each check prints PASS or FAIL: reason. Run as root in the lab container.
on() { m=$1; shift; ip netns exec "$m" "$@"; }
check_download() {
  got=$(on office curl -s --max-time 15 http://10.0.2.20/pricelist.csv | sha256sum | cut -d' ' -f1)
  [ "$got" = "$(cat /var/lib/pricelist.sha256)" ] && echo PASS || echo "FAIL: the price list doesn't arrive whole in 15 s"; }
check_pmtu() {
  for m in office r1 r2 web files printer; do
    on $m ip route show table all | grep -q ' mtu ' && { echo "FAIL: a route on $m carries an mtu"; return; }
  done
  want="office:eth0:1500 r1:eth0:1500 r1:wan:1500 r1:gre1:1476 r2:wan:1500 r2:gre1:1476 r2:lan:1500 web:eth0:1500 files:eth0:1500"
  for w in $want; do IFS=: read -r m i v <<< "$w"
    got=$(on $m cat /sys/class/net/$i/mtu 2>/dev/null); [ "$got" = "$v" ] || { echo "FAIL: $m $i mtu is $got"; return; }; done
  [ "$(on web sysctl -n net.ipv4.ip_no_pmtu_disc)" = 0 ] || { echo "FAIL: web doesn't do path MTU discovery"; return; }
  a=10.0.1.$((128 + RANDOM % 127))
  out=$(on web ping -c1 -W2 -M do -s 1472 "$a" 2>&1)
  echo "$out" | grep -Eq 'mtu ?= ?1476' && echo PASS || echo "FAIL: web isn't told the path's MTU"; }
check_strict() {
  for p in 22 8080 3306; do on web timeout 6 nc -l -p $p >/dev/null 2>&1 & done; sleep 0.5
  on office nc -z -w2 10.0.2.20 80 2>/dev/null || { echo "FAIL: port 80 doesn't answer"; return; }
  bad=""; for p in 22 8080 3306; do s=$(date +%s%N); if on office nc -z -w2 10.0.2.20 $p 2>/dev/null; then bad="$bad $p(open)"; fi
    e=$(( ($(date +%s%N) - s) / 1000000 )); [ $e -lt 1500 ] && bad="$bad $p(answered in ${e}ms)"; done
  wait; [ -z "$bad" ] && echo PASS || echo "FAIL: web answers on$bad"; }
check_files() { [ "$(on office curl -s --max-time 5 http://10.0.2.30/)" = files ] && echo PASS || echo "FAIL: files doesn't answer"; }
check_printer() { on office ping -c1 -W2 10.0.3.5 >/dev/null && echo PASS || echo "FAIL: the printer doesn't answer"; }
check_lasts() {
  netlab-down chk- 2>/dev/null; netlab-up chk- >/dev/null 2>&1 || { echo "FAIL: the config doesn't build"; netlab-down chk-; return; }
  for m in office r1 r2 web files printer; do
    if ! diff <(netlab-state $m) <(netlab-state chk-$m) > /tmp/d 2>&1; then echo "FAIL: $m differs from its config: $(head -3 /tmp/d | tr '\n' ' ')"; netlab-down chk-; return; fi
  done
  on chk-web timeout 5 nc -l -p 80 >/dev/null 2>&1 & sleep 0.3
  on chk-office nc -z -w2 10.0.2.20 80 2>/dev/null || { echo "FAIL: built fresh, office can't reach web"; netlab-down chk-; return; }
  for t in 10.0.2.30 10.0.3.5; do on chk-office ping -c1 -W2 $t >/dev/null || { echo "FAIL: built fresh, office can't reach $t"; netlab-down chk-; return; }; done
  out=$(on chk-web ping -c1 -W2 -M do -s 1472 10.0.1.$((128 + RANDOM % 127)) 2>&1); netlab-down chk-
  echo "$out" | grep -Eq 'mtu ?= ?1476' && echo PASS || echo "FAIL: built fresh, web isn't told the path's MTU"; }
for c in download pmtu strict files printer lasts; do printf '%-9s %s\n' "$c" "$(check_$c)"; done
