#!/bin/bash
# Prototype checks for topic 25's debug. Each prints PASS or FAIL: reason.
on() { m=$1; shift; ip netns exec "$m" "$@"; }
g6() { on "$1" ip -6 -o addr show dev eth0 scope global | awk '{print $4}'; }
check_slaac() {
  for h in h1 h2; do
    a=$(on $h ip -6 -o addr show dev eth0 scope global dynamic | awk '{print $4}' | head -1)
    [ -n "$a" ] || { echo "FAIL: $h has no global IPv6 address it made itself"; return; }
    python3 -c "import ipaddress,sys; sys.exit(0 if ipaddress.ip_interface(sys.argv[1]).network == ipaddress.ip_network('2001:db8:42:a::/64') else 1)" "$a" \
      || { echo "FAIL: $h's address $a isn't in the LAN's /64"; return; }
    on $h ip -6 -o addr show dev eth0 scope global permanent | grep -q . && { echo "FAIL: $h has an address typed in by hand"; return; }
  done
  echo PASS
}
check_reach() {
  a=$(g6 h1 | head -1 | cut -d/ -f1)
  for _ in 1 2 3 4 5; do got=$(on h1 nc -6 -w3 2001:db8:80::80 8080 < /dev/null 2> /dev/null); [ -n "$got" ] && break; sleep 1; done
  [ -n "$a" ] && [ "$got" = "$a" ] && echo PASS || echo "FAIL: web sees h1 as [$got], not as h1's own address [$a]"
}
check_v4() {
  got=$(on h1 nc -4 -w3 203.0.113.80 8080 < /dev/null 2> /dev/null)
  [ "$got" = 198.51.100.2 ] && echo PASS || echo "FAIL: IPv4 from h1 reaches web as [$got]"
}
check_upload() {
  got=$(on h1 timeout 15 bash -c 'nc -6 -N -w 10 2001:db8:80::80 9000 < /var/lib/upload.bin' 2>/dev/null)
  [ "$got" = 2000000 ] && echo PASS || echo "FAIL: a 2 MB upload over IPv6 didn't arrive whole"
}
check_ptb() {
  for w in h1:eth0 h2:eth0 r1:lan r1:wan isp:cust; do
    IFS=: read -r m i <<< "$w"
    [ "$(on $m cat /sys/class/net/$i/mtu)" = 1500 ] || { echo "FAIL: $m $i mtu changed"; return; }
  done
  out=$(on h1 ping -6 -c1 -W2 -M do -s 1452 "2001:db8:80::1$((RANDOM % 900 + 100))" 2>&1)
  echo "$out" | grep -Eq 'mtu ?= ?1400' && echo PASS || echo "FAIL: h1 isn't told the path's MTU"
}
check_egress_only() {
  bad=""
  for h in h1 h2; do
    a=$(g6 $h | head -1 | cut -d/ -f1)
    [ -n "$a" ] || continue
    for p in 22 80 8080; do on $h timeout 5 nc -6 -l -p $p > /dev/null 2>&1 & done
    sleep 0.4
    for p in 22 80 8080; do on web nc -6 -z -w2 "$a" $p 2> /dev/null && bad="$bad $h:$p"; done
    wait
  done
  [ -z "$bad" ] && echo PASS || echo "FAIL: the internet opened connections to$bad"
}
check_lasts() {
  netlab-down chk- 2> /dev/null
  netlab-up chk- > /dev/null 2>&1 || { echo "FAIL: the config doesn't build"; netlab-down chk-; return; }
  for m in h1 h2 r1 isp core web; do
    if ! diff <(netlab-state $m) <(netlab-state chk-$m) > /tmp/d 2>&1; then
      echo "FAIL: $m differs from its config: $(head -4 /tmp/d | tr '\n' ' ')"; netlab-down chk-; return
    fi
  done
  netlab-down chk-
  echo PASS
}
for c in slaac reach v4 upload ptb egress_only lasts; do printf '%-12s %s\n' "$c" "$(check_$c)"; done
