on office traceroute -n -w 1 -q 1 -m 4 10.3.0.10
on r1 vtysh -c 'show ip route'
on r1 ip route get 10.3.0.10
on r1 vtysh -c 'configure terminal' -c 'ip route 10.3.0.0/24 10.0.13.2' -c 'end'
on office traceroute -n -w 1 -q 1 -m 4 10.3.0.10
on dc timeout 4 tcpdump -nn -i eth0 icmp & sleep 1
on office ping -c 2 -W 1 10.3.0.10
wait
on r3 vtysh -c 'configure terminal' -c 'ip route 10.1.0.0/24 10.0.13.1' -c 'end'
on office ping -c 2 -W 1 10.3.0.10
on office curl -sS -m 3 http://10.3.0.10/
on r1 vtysh -c 'configure terminal' -c 'ip route 10.3.0.128/25 10.0.12.2' -c 'end'
on r1 ip route get 10.3.0.10
on r1 ip route get 10.3.0.200
on r1 vtysh -c 'configure terminal' -c 'no ip route 10.3.0.128/25 10.0.12.2' -c 'end'
on r1 vtysh -c 'configure terminal' -c 'ip route 10.3.0.0/24 10.0.12.2 200' -c 'ip route 10.2.0.0/24 10.0.12.2' -c 'ip route 10.2.0.0/24 10.0.13.2 200' -c 'end'
on r2 vtysh -c 'configure terminal' -c 'ip route 10.1.0.0/24 10.0.12.1' -c 'ip route 10.1.0.0/24 10.0.23.2 200' -c 'ip route 10.3.0.0/24 10.0.23.2' -c 'ip route 10.3.0.0/24 10.0.12.1 200' -c 'end'
on r3 vtysh -c 'configure terminal' -c 'ip route 10.1.0.0/24 10.0.23.1 200' -c 'ip route 10.2.0.0/24 10.0.23.1' -c 'ip route 10.2.0.0/24 10.0.13.1 200' -c 'end'
on r1 vtysh -c 'show ip route'
on r1 ip route
sudo netlab link r1 r3 down
on office traceroute -n -w 1 -q 1 -m 5 10.3.0.10
on r1 vtysh -c 'show ip route 10.3.0.0/24'
sudo netlab link r1 r3 up
sudo netlab link r1 r3 silent
on office ping -c 3 -W 1 10.3.0.10
on r1 vtysh -c 'show ip route 10.3.0.0/24'
sudo netlab link r1 r3 restore
for r in r1 r2 r3; do on "$r" vtysh -c 'write memory'; done
on r1 cat /etc/frr/frr.conf
