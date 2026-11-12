# Wrong: all three faults fixed, and the forward chain's policy turned to
# accept along the way "to rule the firewall out", so gw forwards anything
# into the shop's network from anyone who can route to it.
sudo sed -i -e 's/snat to 198.51.100.3:40000-40049/snat to 198.51.100.3/' \
  -e '/# Anything else./d' -e '/iifname "wan" masquerade/d' \
  -e 's#ip saddr 10.1.1.0/24#ip saddr 10.1.0.0/24#' \
  -e 's/hook forward priority filter; policy drop;/hook forward priority filter; policy accept;/' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
