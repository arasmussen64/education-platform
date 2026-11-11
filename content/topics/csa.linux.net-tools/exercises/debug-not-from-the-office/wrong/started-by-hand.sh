# Wrong: the name and the firewall are fixed, but the API's unit is left as
# it was. The service is stopped and a copy of the program is started by
# hand, which listens on every address, so the office is answered until the
# next reboot, when systemd starts the unit as it was and the ticket is back.
sudo sed -i 's/^host-record=shop.internal,.*/host-record=shop.internal,10.0.9.1/' /etc/dnsmasq.d/shop.conf && sudo systemctl restart dnsmasq
sudo sed -i 's/{ 22, 8000 }/{ 22, 8080 }/' /etc/nftables.conf && sudo nft -f /etc/nftables.conf
sudo systemctl stop shop-api
sudo -u shop setsid nohup /usr/local/bin/shop-api > /dev/null 2>&1 &
sleep 2
from-office curl -s -m 5 http://shop.internal:8080/
