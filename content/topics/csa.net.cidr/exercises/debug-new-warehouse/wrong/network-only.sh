# Wrong: all three faults are fixed in the network, but the plan still
# gives the warehouse 10.1.3.0/23, so the plan and the network disagree,
# and the next person to read the plan is misled.
on till sed -i 's#10.1.1.20/16#10.1.1.20/24#' /etc/network/up
on r1 sed -i 's#10.1.3.1/23#10.1.4.1/23#' /etc/network/up
on scan sed -i 's#10.1.3.40/23#10.1.4.40/23#; s#via 10.1.3.1$#via 10.1.4.1#' /etc/network/up
on r2 sed -i 's#10.1.0.0/22#10.1.0.0/20#' /etc/network/up
sudo netlab restart
