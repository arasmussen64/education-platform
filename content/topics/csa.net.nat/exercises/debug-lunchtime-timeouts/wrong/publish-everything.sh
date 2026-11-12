# Wrong: all three faults fixed, and a rule added that sends every other
# port arriving on 198.51.100.2 to the app as well, "so nothing is blocked",
# which publishes the app's database and SSH to the internet.
sudo sed -i -e 's/snat to 198.51.100.3:40000-40049/snat to 198.51.100.3/' \
  -e '/# Anything else./d' -e '/iifname "wan" masquerade/d' \
  -e 's#ip saddr 10.1.1.0/24#ip saddr 10.1.0.0/24#' \
  -e 's#tcp dport 443 dnat to 10.1.0.20:8443#tcp dport 443 dnat to 10.1.0.20:8443\n        iifname "wan" ip daddr 198.51.100.2 dnat to 10.1.0.20#' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
