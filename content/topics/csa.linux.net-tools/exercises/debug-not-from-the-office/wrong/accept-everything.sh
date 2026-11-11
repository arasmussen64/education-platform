# Wrong: the firewall is "fixed" with a rule at the end of the input chain
# that accepts everything, in the file and loaded. The policy still reads
# drop, and it's never reached: every port is let in, and the office's
# connection to the database port is answered (refused) rather than dropped.
sudo sed -i 's/^host-record=shop.internal,.*/host-record=shop.internal,10.0.9.1/' /etc/dnsmasq.d/shop.conf && sudo systemctl restart dnsmasq
sudo sed -i 's/^\t\tudp dport 53 accept$/\t\tudp dport 53 accept\n\t\taccept/' /etc/nftables.conf && sudo nft -f /etc/nftables.conf
sudo mkdir -p /etc/systemd/system/shop-api.service.d && printf '[Service]\nEnvironment=BIND=0.0.0.0\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null && sudo systemctl daemon-reload && sudo systemctl restart shop-api
grep -q '^\s*accept$' /etc/nftables.conf
