# Wrong: the gaps filled, and the forward chain's policy turned to accept "to
# make it work", so gw forwards anything at all into the shop's network from
# anyone who can route to it.
sudo sed -i -e 's/ct status ___/ct status dnat/' -e 's/dnat to ___/dnat to 10.1.0.20:8443/' \
  -e 's/hook ___ priority ___/hook postrouting priority srcnat/' -e 's/oifname "___"/oifname "wan"/' \
  -e 's/hook forward priority filter; policy drop;/hook forward priority filter; policy accept;/' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
