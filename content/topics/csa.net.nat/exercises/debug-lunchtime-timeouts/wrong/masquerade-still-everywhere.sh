# Wrong: the payments and the office fixed, and the catch-all masquerade's
# iifname "wan" taken out rather than turned round, so it now rewrites
# everything gw sends anywhere, customers' connections going in to the app
# included: the app still sees every customer as 10.1.0.1.
sudo sed -i -e 's/snat to 198.51.100.3:40000-40049/snat to 198.51.100.3/' \
  -e 's/iifname "wan" masquerade/masquerade/' \
  -e 's#ip saddr 10.1.1.0/24#ip saddr 10.1.0.0/24#' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
