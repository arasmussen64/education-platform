# Wrong: the warehouse is moved to a free, aligned /23, 10.1.32.0/23, but
# outside HQ's block, 10.1.0.0/20, so the branch's one route to HQ doesn't
# cover it. The other two faults are fixed.
on till sed -i 's#10.1.1.20/16#10.1.1.20/24#' /etc/network/up
sudo sed -i 's#^warehouse .*#warehouse   10.1.32.0/23#' /etc/netlab/plan.txt
on r1 sed -i 's#10.1.3.1/23#10.1.32.1/23#' /etc/network/up
on scan sed -i 's#10.1.3.40/23#10.1.32.40/23#; s#via 10.1.3.1$#via 10.1.32.1#' /etc/network/up
on r2 sed -i 's#10.1.0.0/22#10.1.0.0/20#' /etc/network/up
sudo netlab restart
