# Wrong: the warehouse is moved to 10.1.5.0/23, which overlaps nothing
# the plan lists, so everything is reachable; but 10.1.5.0 isn't the start
# of a /23 either (the kernel makes it 10.1.4.0/23), so the plan names a
# block that doesn't exist as written. The other two faults are fixed.
on till sed -i 's#10.1.1.20/16#10.1.1.20/24#' /etc/network/up
sudo sed -i 's#^warehouse .*#warehouse   10.1.5.0/23#' /etc/netlab/plan.txt
on r1 sed -i 's#10.1.3.1/23#10.1.5.1/23#' /etc/network/up
on scan sed -i 's#10.1.3.40/23#10.1.5.40/23#; s#via 10.1.3.1$#via 10.1.5.1#' /etc/network/up
on r2 sed -i 's#10.1.0.0/22#10.1.0.0/20#' /etc/network/up
sudo netlab restart
