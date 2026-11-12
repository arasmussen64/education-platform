# Prototype of part 2's per-tunnel check (replaces the ip-route-get prediction,
# which proved wrong). Twenty connections from the office to app2 from fresh
# source ports above Linux's ephemeral range (so nothing else uses them, and a
# range that moves with the clock so a re-run within a minute finds no
# TIME-WAIT), with a capture on each of r2's tunnels. Every connection must
# bring the whole catalogue, and each tunnel must have carried at least one of
# them: a filter on one tunnel either drops some (a failure) or, if by chance
# none were sent its way, leaves that tunnel unused (also a failure).
. /usr/local/lib/netlab/checklib.sh
want=$(sha256sum /srv/www/catalog | cut -d' ' -f1)
lo=$((61000 + ($(date +%s) % 40) * 25)); hi=$((lo + 19))
filter="tcp[tcpflags] & tcp-syn != 0 and src host 10.10.0.10 and src portrange $lo-$hi"
for t in tun1 tun2; do
  on r2 timeout 25 tcpdump -nn -U -Z root -i $t -w /tmp/check-$t.pcap "$filter" > /dev/null 2>&1 &
done
sleep 1
bad=0
for p in $(seq $lo $hi); do
  got=$(on pc curl -s --local-port $p --max-time 3 -H 'Host: www.shop.test' http://10.30.0.11/catalog | sha256sum | cut -d' ' -f1)
  [ "$got" = "$want" ] || bad=$((bad + 1))
done
sleep 1
on r2 pkill -x tcpdump 2>/dev/null; wait
n1=$(tcpdump -nn -r /tmp/check-tun1.pcap 2>/dev/null | wc -l)
n2=$(tcpdump -nn -r /tmp/check-tun2.pcap 2>/dev/null | wc -l)
rm -f /tmp/check-tun1.pcap /tmp/check-tun2.pcap
echo "debug: failed=$bad tun1=$n1 tun2=$n2" >&2
[ "$bad" -eq 0 ] || { echo "from the office, $bad of 20 connections to app2 didn't bring the whole catalogue"; exit 0; }
[ "$n1" -gt 0 ] && [ "$n2" -gt 0 ] || { echo "the office's connections to app2 didn't go over both tunnels"; exit 0; }
echo "both tunnels carry it"
