# Wrong: the gaps filled, and a second rule added after the published port
# that sends every other port arriving on wan to the app as well, so the
# app's database and SSH answer from the internet.
sudo sed -i -e 's/ct status ___/ct status dnat/' -e 's/dnat to ___/dnat to 10.1.0.20:8443\n        iifname "wan" dnat to 10.1.0.20/' \
  -e 's/hook ___ priority ___/hook postrouting priority srcnat/' -e 's/oifname "___"/oifname "wan"/' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
