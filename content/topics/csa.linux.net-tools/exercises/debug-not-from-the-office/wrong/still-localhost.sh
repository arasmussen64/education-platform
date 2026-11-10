# Wrong: the name and the firewall are fixed, but the API still listens on
# 127.0.0.1 only, so the office's connection is refused.
sudo sed -i 's/^host-record=shop.internal,.*/host-record=shop.internal,10.0.9.1/' /etc/dnsmasq.d/shop.conf && sudo systemctl restart dnsmasq
sudo sed -i 's/{ 22, 8000 }/{ 22, 8080 }/' /etc/nftables.conf && sudo nft -f /etc/nftables.conf
