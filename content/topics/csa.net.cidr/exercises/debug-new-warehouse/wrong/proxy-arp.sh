# Wrong: the warehouse and r2's route are fixed, and the till's /16 is left
# alone: r1 is made to answer ARP on the store's switch for every address
# it can route elsewhere (proxy ARP), in its sysctl.d so it lasts. The till
# reaches everything, because r1 answers for the printer, the server and
# the kiosk, but r1 now answers ARP for addresses that aren't its own, and
# the till still has the wrong prefix.
sudo sed -i 's#^warehouse .*#warehouse   10.1.4.0/23#' /etc/netlab/plan.txt
on r1 sed -i 's#10.1.3.1/23#10.1.4.1/23#' /etc/network/up
on scan sed -i 's#10.1.3.40/23#10.1.4.40/23#; s#via 10.1.3.1$#via 10.1.4.1#' /etc/network/up
on r2 sed -i 's#10.1.0.0/22#10.1.0.0/20#' /etc/network/up
echo 'net.ipv4.conf.store.proxy_arp = 1' | on r1 tee /etc/sysctl.d/90-proxy-arp.conf > /dev/null
sudo netlab restart
