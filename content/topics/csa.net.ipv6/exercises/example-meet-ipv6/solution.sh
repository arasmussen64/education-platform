netlab show
on r1 cat /etc/network/up
on r1 cat /etc/sysctl.d/90-forward.conf
on r1 cat /etc/radvd.conf
on h1 ip -6 addr show dev eth0
on h1 cat /sys/class/net/eth0/address
on h1 ip -6 route
on r1 ip -6 addr show dev lan scope link
mkdir -p ~/example; m=$(on h2 cat /sys/class/net/eth0/address); echo "$m"
on r1 timeout 6 tcpdump -nn -l -i lan "icmp6 and ether host $m" > ~/example/slaac.txt &
sleep 1; on h2 sysctl -w net.ipv6.conf.eth0.disable_ipv6=1; on h2 sysctl -w net.ipv6.conf.eth0.disable_ipv6=0; wait
cat ~/example/slaac.txt
on h2 ip -6 addr show dev eth0
on h1 ping -6 -c 1 2001:db8:80::80
on h1 ip -6 neigh
on h1 getent ahosts web.shop.test
on h1 nc -w 3 web.shop.test 8080 < /dev/null | tee ~/example/whoami6.txt
on h1 nc -4 -w 3 web.shop.test 8080 < /dev/null | tee ~/example/whoami4.txt
on r1 cat /etc/nftables.conf
a=$(on h1 ip -6 -o addr show dev eth0 scope global | awk '{print $4}' | cut -d/ -f1); echo "$a"
on h1 timeout 5 nc -6 -l -p 22 &
sleep 1; on web nc -6 -z -v -w 2 "$a" 22; echo "exit status $?"; wait
on h1 ping -6 -c 1 -M do -s 1452 2001:db8:80::80
on h1 ip -6 route get 2001:db8:80::80
ls ~/example
