# Wrong: all three faults fixed, and the payment rule loosened "so nothing
# on the way to the provider can miss it": it no longer names the app, so
# whatever the shop sends to the provider's port 443 leaves from
# 198.51.100.3, an office PC's connections included.
sudo sed -i -e 's/ip saddr 10.1.0.20 ip daddr 203.0.113.10 tcp dport 443 snat to 198.51.100.3:40000-40049/ip daddr 203.0.113.10 tcp dport 443 snat to 198.51.100.3/' \
  -e '/# Anything else./d' -e '/iifname "wan" masquerade/d' \
  -e 's#ip saddr 10.1.1.0/24#ip saddr 10.1.0.0/24#' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
