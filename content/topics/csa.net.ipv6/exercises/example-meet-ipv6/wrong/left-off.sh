# Wrong: the evidence is all there, but IPv6 was switched off on h2 again
# afterwards and never switched back on, so h2 is left with no IPv6.
mkdir -p ~/example; m=$(on h2 cat /sys/class/net/eth0/address)
on r1 timeout 6 tcpdump -nn -l -i lan "icmp6 and ether host $m" > ~/example/slaac.txt &
sleep 1; on h2 sysctl -w net.ipv6.conf.eth0.disable_ipv6=1; on h2 sysctl -w net.ipv6.conf.eth0.disable_ipv6=0; wait
on h1 nc -w 3 web.shop.test 8080 < /dev/null > ~/example/whoami6.txt
on h1 nc -4 -w 3 web.shop.test 8080 < /dev/null > ~/example/whoami4.txt
on h2 sysctl -w net.ipv6.conf.eth0.disable_ipv6=1
