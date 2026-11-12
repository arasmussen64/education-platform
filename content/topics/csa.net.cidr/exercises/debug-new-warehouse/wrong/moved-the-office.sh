# Wrong: the warehouse's block is written at its real start, 10.1.2.0/23,
# and the office, which it overlapped, is moved out of its way to
# 10.1.6.0/24 with its printer. The plan is sound and everything is
# reachable, but the office was in use: its block and the printer's
# address had to stay. The other two faults are fixed.
on till sed -i 's#10.1.1.20/16#10.1.1.20/24#' /etc/network/up
sudo sed -i 's#^warehouse .*#warehouse   10.1.2.0/23#; s#^office .*#office      10.1.6.0/24#' /etc/netlab/plan.txt
on r1 sed -i 's#10.1.2.1/24#10.1.6.1/24#' /etc/network/up
on printer sed -i 's#10.1.2.30/24#10.1.6.30/24#; s#via 10.1.2.1$#via 10.1.6.1#' /etc/network/up
on r2 sed -i 's#10.1.0.0/22#10.1.0.0/20#' /etc/network/up
sudo netlab restart
