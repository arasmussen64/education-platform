# Wrong: the till's /16 is taken out of its own file, and its address is
# written into the topology instead (the lab's cables, which are scenery).
# The network works and a fresh build matches it, but the till's own file
# no longer gives it an address, and the next person to read the till's
# settings won't find one. The other two faults are fixed in their files.
sudo sed -i 's#till:eth0$#till:eth0=10.1.1.20/24#' /etc/netlab/topology
on till sed -i '/10.1.1.20\/16/d' /etc/network/up
sudo sed -i 's#^warehouse .*#warehouse   10.1.4.0/23#' /etc/netlab/plan.txt
on r1 sed -i 's#10.1.3.1/23#10.1.4.1/23#' /etc/network/up
on scan sed -i 's#10.1.3.40/23#10.1.4.40/23#; s#via 10.1.3.1$#via 10.1.4.1#' /etc/network/up
on r2 sed -i 's#10.1.0.0/22#10.1.0.0/20#' /etc/network/up
sudo netlab restart
