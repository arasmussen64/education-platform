# Wrong: two of the three faults fixed (the payment range and the catch-all
# masquerade, taken out), but the office's rule still names its old network,
# so office PCs still leave untranslated and their replies never come back.
sudo sed -i -e 's/snat to 198.51.100.3:40000-40049/snat to 198.51.100.3/' \
  -e '/# Anything else./d' -e '/iifname "wan" masquerade/d' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
