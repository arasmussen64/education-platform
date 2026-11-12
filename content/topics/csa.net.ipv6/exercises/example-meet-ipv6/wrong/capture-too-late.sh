# Wrong: h2 restarted its IPv6 before the capture began, so the capture
# saw none of it: no router solicitation, no duplicate address detection.
mkdir -p ~/example; m=$(on h2 cat /sys/class/net/eth0/address)
on h2 sysctl -w net.ipv6.conf.eth0.disable_ipv6=1; on h2 sysctl -w net.ipv6.conf.eth0.disable_ipv6=0
sleep 3
on r1 timeout 4 tcpdump -nn -l -i lan "icmp6 and ether host $m" > ~/example/slaac.txt
on h1 nc -w 3 web.shop.test 8080 < /dev/null > ~/example/whoami6.txt
on h1 nc -4 -w 3 web.shop.test 8080 < /dev/null > ~/example/whoami4.txt
