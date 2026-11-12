# Wrong: r2 is fixed, and web's firewall is switched off for good ("the
# firewall must be broken, turn it off"), so the download works but web
# answers on every port.
on r2 sed -i '/10.0.2.30 lladdr/d; /ip link set prn down/d' /etc/network/up
sudo systemctl disable nftables@web 2> /dev/null
sudo netlab restart
