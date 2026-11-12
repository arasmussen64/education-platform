# Wrong: r2 is fixed, and web's default route gets an MTU of 1476, so its
# packets fit the tunnel. The download works, but the rules say no MTU
# changes, and web still never hears "fragmentation needed".
on r2 sed -i '/10.0.2.30 lladdr/d; /ip link set prn down/d' /etc/network/up
on web sed -i 's/^ip route add default via 10.0.2.1$/ip route add default via 10.0.2.1 mtu 1476/' /etc/network/up
sudo netlab restart
