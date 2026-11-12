# Wrong: the customers' and the office's faults fixed, and the app's two
# rules replaced by one that sends everything the app does out from
# 198.51.100.3, "so payments can't miss it". Payments open, but the app's
# other traffic now leaves from the payments address too, not 198.51.100.2.
sudo sed -i -e '/snat to 198.51.100.3:40000-40049/d' \
  -e 's/ip saddr 10.1.0.20 snat to 198.51.100.2/ip saddr 10.1.0.20 snat to 198.51.100.3/' \
  -e '/# Anything else./d' -e '/iifname "wan" masquerade/d' \
  -e 's#ip saddr 10.1.1.0/24#ip saddr 10.1.0.0/24#' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
