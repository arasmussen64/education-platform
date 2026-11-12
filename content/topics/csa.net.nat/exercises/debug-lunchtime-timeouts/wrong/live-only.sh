# Wrong: all three faults fixed in the running rules only, loaded from a
# fixed copy, while gw's /etc/nftables.conf keeps them, so the next boot
# brings all three back.
sed -e 's/snat to 198.51.100.3:40000-40049/snat to 198.51.100.3/' \
  -e '/# Anything else./d' -e '/iifname "wan" masquerade/d' \
  -e 's#ip saddr 10.1.1.0/24#ip saddr 10.1.0.0/24#' /etc/netns/gw/nftables.conf > /tmp/gw-rules.nft
on gw nft -f /tmp/gw-rules.nft
rm -f /tmp/gw-rules.nft
