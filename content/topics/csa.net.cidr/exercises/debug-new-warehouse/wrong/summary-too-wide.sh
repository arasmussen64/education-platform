# Wrong: r2's route to HQ is widened to 10.1.0.0/19, which covers every
# HQ network, and the branch's own 10.1.16.0/24 as well. Everything is
# reachable, because r2's own, more specific route to the branch wins; but
# the route is wider than HQ's block, so the day the branch's switch is
# down, r2 sends the branch's traffic to HQ.
on till sed -i 's#10.1.1.20/16#10.1.1.20/24#' /etc/network/up
sudo sed -i 's#^warehouse .*#warehouse   10.1.4.0/23#' /etc/netlab/plan.txt
on r1 sed -i 's#10.1.3.1/23#10.1.4.1/23#' /etc/network/up
on scan sed -i 's#10.1.3.40/23#10.1.4.40/23#; s#via 10.1.3.1$#via 10.1.4.1#' /etc/network/up
on r2 sed -i 's#10.1.0.0/22#10.1.0.0/19#' /etc/network/up
sudo netlab restart
