# Wrong: the neighbour tables were not emptied first. The laptop had just
# talked to its gateway (the curl), so it still knew the gateway's MAC
# address and sent no ARP request: the capture has no ARP in it.
on office curl -s http://10.0.2.20/
mkdir -p ~/example
on r1 timeout 4 tcpdump -e -nn -v -i eth0 'arp or icmp' > ~/example/office-side.txt &
on r2 timeout 4 tcpdump -e -nn -v -i lan 'arp or icmp' > ~/example/cloud-side.txt &
sleep 1; on office ping -c 1 10.0.2.20; wait
on r1 timeout 5 tcpdump -nn -xx -c 1 -i eth0 icmp > ~/example/hex.txt &
sleep 1; on office ping -c 1 10.0.2.20 > /dev/null; wait
on r1 timeout 5 tcpdump -nn -v -c 2 -i wan > ~/example/wan.txt &
sleep 1; on office ping -c 1 10.0.2.20 > /dev/null; wait
on office tracepath -n 10.0.2.20 > ~/example/pmtu.txt
