#!/bin/bash
echo "== reset mode, -v capture on lab's eth1"
timeout 50 tcpdump -nn -v -i eth1 -l 'tcp port 5432 and (tcp[tcpflags] & (tcp-rst|tcp-syn) != 0)' > /tmp/ttl.txt 2>/dev/null &
sleep 0.5; python3 /proto/client.py 35 off; sleep 1; kill %1; sleep 0.3; cat /tmp/ttl.txt
echo "== switch to drop mode"
ip netns exec nat nft flush chain inet gateway forward
ip netns exec nat nft add rule inet gateway forward ct state established,related accept
ip netns exec nat nft add rule inet gateway forward iifname in0 tcp flags syn / syn,ack ct state new accept
ip netns exec nat nft add rule inet gateway forward iifname in0 drop
timeout 60 tcpdump -nn -i eth1 -l tcp port 5432 > /tmp/drop.txt 2>/dev/null &
sleep 0.5; python3 /proto/client.py 35 off; sleep 1; kill %1; sleep 0.3; tail -8 /tmp/drop.txt
ss -tno | grep 5432
