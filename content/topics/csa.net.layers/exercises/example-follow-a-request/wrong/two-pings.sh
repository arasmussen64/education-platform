# Wrong: each side was captured during a ping of its own, one after the
# other, so the two files hold two different packets (their IP
# identification numbers differ), not one packet seen twice.
mkdir -p ~/example; for m in office r1 r2 web; do on $m ip neigh flush all; done
on r1 timeout 4 tcpdump -e -nn -v -i eth0 'arp or icmp' > ~/example/office-side.txt &
sleep 1; on office ping -c 1 10.0.2.20; wait
on r2 timeout 4 tcpdump -e -nn -v -i lan 'arp or icmp' > ~/example/cloud-side.txt &
sleep 1; on office ping -c 1 10.0.2.20; wait
on r1 timeout 5 tcpdump -nn -xx -c 1 -i eth0 icmp > ~/example/hex.txt &
sleep 1; on office ping -c 1 10.0.2.20 > /dev/null; wait
on r1 timeout 5 tcpdump -nn -v -c 2 -i wan > ~/example/wan.txt &
sleep 1; on office ping -c 1 10.0.2.20 > /dev/null; wait
on office tracepath -n 10.0.2.20 > ~/example/pmtu.txt
