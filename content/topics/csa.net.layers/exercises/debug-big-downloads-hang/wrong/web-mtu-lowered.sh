# Wrong: r2 is fixed, and web's network card gets the tunnel's MTU, so its
# packets fit the tunnel. The download works, but the rules say no MTU
# changes, and web still never hears "fragmentation needed".
on r2 sed -i '/10.0.2.30 lladdr/d; /ip link set prn down/d' /etc/network/up
echo 'ip link set eth0 mtu 1476' | on web tee -a /etc/network/up > /dev/null
sudo netlab restart
