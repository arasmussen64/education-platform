# Wrong: the published port is sent to the app's address with no port, so
# port 443 goes on to the app's port 443, where nothing listens.
sudo sed -i -e 's/ct status ___/ct status dnat/' -e 's/dnat to ___/dnat to 10.1.0.20/' \
  -e 's/hook ___ priority ___/hook postrouting priority srcnat/' -e 's/oifname "___"/oifname "wan"/' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
