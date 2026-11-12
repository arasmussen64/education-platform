# Wrong: the warehouse stays at 10.1.3 but shrinks to a /24, which is
# aligned and overlaps nothing, so everything is reachable; but a /24 has
# room for 254 machines, not the 400 scanners the warehouse needs. The
# other two faults are fixed.
on till sed -i 's#10.1.1.20/16#10.1.1.20/24#' /etc/network/up
sudo sed -i 's#^warehouse .*#warehouse   10.1.3.0/24#' /etc/netlab/plan.txt
on r1 sed -i 's#10.1.3.1/23#10.1.3.1/24#' /etc/network/up
on scan sed -i 's#10.1.3.40/23#10.1.3.40/24#' /etc/network/up
on r2 sed -i 's#10.1.0.0/22#10.1.0.0/20#' /etc/network/up
sudo netlab restart
