# Wrong: the masquerade rule is limited to the wrong interface, lan, so what
# leaves for the internet isn't translated (the office's replies never come
# back) and what goes in to the app is.
sudo sed -i -e 's/ct status ___/ct status dnat/' -e 's/dnat to ___/dnat to 10.1.0.20:8443/' \
  -e 's/hook ___ priority ___/hook postrouting priority srcnat/' -e 's/oifname "___"/oifname "lan"/' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
