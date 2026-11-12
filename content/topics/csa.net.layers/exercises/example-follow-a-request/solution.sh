netlab show
cat /etc/netlab/topology
on office ip -br addr
systemctl status nginx@web --no-pager
on r1 cat /etc/network/up
on office ip route
on r1 ip route
on office curl -s http://10.0.2.20/
mkdir -p ~/example; for m in office r1 r2 web; do on $m ip neigh flush all; done
on r1 timeout 4 tcpdump -e -nn -v -i eth0 'arp or icmp' > ~/example/office-side.txt &
on r2 timeout 4 tcpdump -e -nn -v -i lan 'arp or icmp' > ~/example/cloud-side.txt &
sleep 1; on office ping -c 1 10.0.2.20; wait
cat ~/example/office-side.txt
cat ~/example/cloud-side.txt
on r1 timeout 5 tcpdump -nn -xx -c 1 -i eth0 icmp > ~/example/hex.txt &
sleep 1; on office ping -c 1 10.0.2.20 > /dev/null; wait; cat ~/example/hex.txt
on r1 timeout 10 tshark -V -c 1 -i eth0 icmp &
sleep 3; on office ping -c 3 10.0.2.20 > /dev/null; wait
on r1 timeout 5 tcpdump -nn -v -c 2 -i wan > ~/example/wan.txt &
sleep 1; on office ping -c 1 10.0.2.20 > /dev/null; wait; cat ~/example/wan.txt
on r1 timeout 5 tcpdump -nn -c 2 -i gre1 &
sleep 1; on office ping -c 1 10.0.2.20 > /dev/null; wait
on office tracepath -n 10.0.2.20 | tee ~/example/pmtu.txt
on office ip route get 10.0.2.20
on office ping -c 1 -M do -s 1448 10.0.2.20
on office ping -c 1 -M do -s 1449 10.0.2.20
on office ping -c 1 -M do -s 1472 10.0.2.1
ls ~/example
