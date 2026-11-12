# Wrong: the customers' and the office's faults fixed, and the payment range
# widened to 130 ports, just above today's peak of 120 but short of the 240
# the business wants room for.
sudo sed -i -e 's/snat to 198.51.100.3:40000-40049/snat to 198.51.100.3:40000-40129/' \
  -e '/# Anything else./d' -e '/iifname "wan" masquerade/d' \
  -e 's#ip saddr 10.1.1.0/24#ip saddr 10.1.0.0/24#' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
