# Wrong: the gaps filled, but the masquerade rule names no interface at all,
# so customers' connections going in to the app are translated too, and the
# app sees every customer as gw's own address on the LAN, 10.1.0.1.
sudo sed -i -e 's/ct status ___/ct status dnat/' -e 's/dnat to ___/dnat to 10.1.0.20:8443/' \
  -e 's/hook ___ priority ___/hook postrouting priority srcnat/' -e 's/oifname "___" masquerade/masquerade/' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
