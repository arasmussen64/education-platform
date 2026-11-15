# Wrong: the payment range and the customers' fault fixed, the second by
# turning the catch-all masquerade round, from iifname "wan" to oifname
# "wan", and the office's rule left naming the office's old network. The
# office's PCs now get out, but only through the catch-all, and masquerade
# takes the first address on wan, 198.51.100.3: the office leaves from the
# payments' address, which the provider's payment port answers.
sudo sed -i -e 's/snat to 198.51.100.3:40000-40049/snat to 198.51.100.3/' \
  -e 's/iifname "wan" masquerade/oifname "wan" masquerade/' /etc/netns/gw/nftables.conf
sudo systemctl restart nftables@gw
