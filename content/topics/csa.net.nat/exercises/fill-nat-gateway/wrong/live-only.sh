# Wrong: the right rules loaded live from a filled-in copy, and gw's file
# itself left with its gaps, so the next boot loads no firewall at all.
sed -e 's/ct status ___/ct status dnat/' -e 's/dnat to ___/dnat to 10.1.0.20:8443/' \
  -e 's/hook ___ priority ___/hook postrouting priority srcnat/' -e 's/oifname "___"/oifname "wan"/' /etc/netns/gw/nftables.conf > /tmp/gw-rules.nft
on gw nft -f /tmp/gw-rules.nft
rm -f /tmp/gw-rules.nft
