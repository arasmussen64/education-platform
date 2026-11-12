# Wrong: the payment rule moved to 198.51.100.2's whole port range, "where
# there are plenty of ports", which the payment provider drops.
sudo sed -i -e 's/snat to 198.51.100.3:40000-40049/snat to 198.51.100.2/' \
  -e '/# Anything else./d' -e '/iifname "wan" masquerade/d' \
  -e 's#ip saddr 10.1.1.0/24#ip saddr 10.1.0.0/24#' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
