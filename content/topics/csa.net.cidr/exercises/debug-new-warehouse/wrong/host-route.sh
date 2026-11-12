# Wrong: the warehouse and r2's route are fixed, and the till keeps its
# /16 with a route through r1 for each network it couldn't reach. Routes
# more specific than the /16 win, so the till reaches everything, but it
# has routes besides its own network and its default, and the wrong
# prefix: the next network added would break it again.
sudo sed -i 's#^warehouse .*#warehouse   10.1.4.0/23#' /etc/netlab/plan.txt
on r1 sed -i 's#10.1.3.1/23#10.1.4.1/23#' /etc/network/up
on scan sed -i 's#10.1.3.40/23#10.1.4.40/23#; s#via 10.1.3.1$#via 10.1.4.1#' /etc/network/up
on r2 sed -i 's#10.1.0.0/22#10.1.0.0/20#' /etc/network/up
on till tee -a /etc/network/up > /dev/null << 'EOF'
ip route add 10.1.2.0/24 via 10.1.1.1
ip route add 10.1.4.0/23 via 10.1.1.1
ip route add 10.1.8.0/24 via 10.1.1.1
ip route add 10.1.16.0/24 via 10.1.1.1
EOF
sudo netlab restart
