# Wrong: the plan is put right (the warehouse at 10.1.4.0/23), but the
# network isn't changed to match it: r1 and the scanner are still on the
# misaligned block, the till still has its /16, and r2 still has its
# narrow route.
sudo sed -i 's#^warehouse .*#warehouse   10.1.4.0/23#' /etc/netlab/plan.txt
