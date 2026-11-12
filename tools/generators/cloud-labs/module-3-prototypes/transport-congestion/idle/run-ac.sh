#!/bin/bash
# assumes mech.sh already ran and server is running in db
echo "== A: keepalive off, idle 40 ($1 mode)"
ip netns exec nat timeout 50 tcpdump -nn -i in0 -l tcp port 5432 > /tmp/capA-$1.txt 2>/dev/null &
sleep 0.5
python3 /proto/client.py 40 off
sleep 1; kill %1 2>/dev/null; sleep 0.5
echo "-- capture A (inside):"; cat /tmp/capA-$1.txt
echo "== C: keepalive on, system default time, idle 40"
python3 /proto/client.py 40 on > /tmp/c.txt 2>&1 &
sleep 2; ss -tno state established "( dport = :5432 )"
wait %2 2>/dev/null; cat /tmp/c.txt
echo "== D: keepalive on, sysctl time 12, idle 40"
sysctl -qw net.ipv4.tcp_keepalive_time=12
python3 /proto/client.py 40 on > /tmp/d.txt 2>&1 &
sleep 2; ss -tno state established "( dport = :5432 )"
wait %3 2>/dev/null; cat /tmp/d.txt
sysctl -qw net.ipv4.tcp_keepalive_time=7200
