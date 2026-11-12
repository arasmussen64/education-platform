# Wrong: the encapsulation capture was taken on the tunnel's own
# interface, gre1, instead of the internet link, wan. On gre1 only the
# inner packet is seen, so wan.txt has no GRE header in it.
mkdir -p ~/example; for m in office r1 r2 web; do on $m ip neigh flush all; done
on r1 timeout 4 tcpdump -e -nn -v -i eth0 'arp or icmp' > ~/example/office-side.txt &
on r2 timeout 4 tcpdump -e -nn -v -i lan 'arp or icmp' > ~/example/cloud-side.txt &
sleep 1; on office ping -c 1 10.0.2.20; wait
on r1 timeout 5 tcpdump -nn -xx -c 1 -i eth0 icmp > ~/example/hex.txt &
sleep 1; on office ping -c 1 10.0.2.20 > /dev/null; wait
on r1 timeout 5 tcpdump -nn -v -c 2 -i gre1 > ~/example/wan.txt &
sleep 1; on office ping -c 1 10.0.2.20 > /dev/null; wait
on office tracepath -n 10.0.2.20 > ~/example/pmtu.txt
