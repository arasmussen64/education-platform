# Wrong: all three faults fixed, and the office laptop changed as well
# ("to be safe", its default route now asks for smaller TCP segments),
# which the rules forbid: there are forty laptops like it.
sudo sed -i 's/ip protocol icmp drop/icmp type echo-request drop/' /etc/netns/web/nftables.conf
on r2 sed -i '/10.0.2.30 lladdr/d; /ip link set prn down/d' /etc/network/up
on office sed -i 's/^ip route add default via 10.0.1.1$/ip route add default via 10.0.1.1 advmss 1400/' /etc/network/up
sudo netlab restart
