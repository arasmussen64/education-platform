#!/bin/bash
# Usage: timeit.sh CONTAINER IMAGE ROUTER PREFIX NPATHS  -- starts a lab container as labcheck does, times boot and BGP convergence
export MSYS_NO_PATHCONV=1
c=$1; img=$2; r=$3; pfx=$4; want=$5
now() { date +%s%N; }; ms() { echo $(( ($2 - $1) / 1000000 )); }
docker rm -f "$c" >/dev/null 2>&1
start=$(now)
docker run -d --name "$c" --hostname lab --privileged --cgroupns=private --tmpfs /run --tmpfs /run/lock "$img" /sbin/init >/dev/null
for i in $(seq 1 240); do s=$(docker exec "$c" systemctl is-system-running 2>/dev/null); case "$s" in running|degraded) break;; esac; sleep 0.25; done
booted=$(now); echo "boot: $s after $(ms $start $booted) ms"
for i in $(seq 1 480); do n=$(docker exec "$c" vtysh -N "$r" -c "show bgp ipv4 unicast $pfx json" 2>/dev/null | grep -c '"valid":true'); [ "$n" -ge "$want" ] && break; sleep 0.25; done
conv=$(now); echo "$r has $n valid paths to $pfx: $(ms $start $conv) ms from docker run, $(ms $booted $conv) ms after boot"
docker exec "$c" systemctl --failed --no-pager --plain | head -3
