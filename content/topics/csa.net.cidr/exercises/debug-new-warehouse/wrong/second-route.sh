# Wrong: r2 keeps its narrow route to HQ and gets one more route for each
# network it didn't cover. The branch reaches everything, but r2 has three
# routes towards HQ where the rules ask for one.
on till sed -i 's#10.1.1.20/16#10.1.1.20/24#' /etc/network/up
sudo sed -i 's#^warehouse .*#warehouse   10.1.4.0/23#' /etc/netlab/plan.txt
on r1 sed -i 's#10.1.3.1/23#10.1.4.1/23#' /etc/network/up
on scan sed -i 's#10.1.3.40/23#10.1.4.40/23#; s#via 10.1.3.1$#via 10.1.4.1#' /etc/network/up
on r2 tee -a /etc/network/up > /dev/null << 'EOF'
ip route add 10.1.4.0/23 via 10.255.2.1
ip route add 10.1.8.0/24 via 10.255.2.1
EOF
sudo netlab restart
