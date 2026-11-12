# Wrong: the plan is put right in its file, but the three faults are fixed
# with live commands only. Everything works until the next boot, which
# builds the machines from their files again.
sudo sed -i 's#^warehouse .*#warehouse   10.1.4.0/23#' /etc/netlab/plan.txt
on till ip addr add 10.1.1.20/24 dev eth0
on till ip addr del 10.1.1.20/16 dev eth0
on till ip route replace default via 10.1.1.1
on r1 ip addr add 10.1.4.1/23 dev warehouse
on r1 ip addr del 10.1.3.1/23 dev warehouse
on scan ip addr add 10.1.4.40/23 dev eth0
on scan ip addr del 10.1.3.40/23 dev eth0
on scan ip route replace default via 10.1.4.1
on r2 ip route replace 10.1.0.0/20 via 10.255.2.1
on r2 ip route del 10.1.0.0/22
