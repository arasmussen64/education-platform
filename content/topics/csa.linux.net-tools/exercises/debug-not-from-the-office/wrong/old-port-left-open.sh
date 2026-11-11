# Wrong: the API's port is added to the firewall beside the old one, which
# stays. The ticket is closed, and so is nothing else: port 8000, which no
# program uses and the office has no need of, is still let in.
sudo sed -i 's/^host-record=shop.internal,.*/host-record=shop.internal,10.0.9.1/' /etc/dnsmasq.d/shop.conf && sudo systemctl restart dnsmasq
sudo sed -i 's/{ 22, 8000 }/{ 22, 8000, 8080 }/' /etc/nftables.conf && sudo nft -f /etc/nftables.conf
sudo mkdir -p /etc/systemd/system/shop-api.service.d && printf '[Service]\nEnvironment=BIND=0.0.0.0\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null && sudo systemctl daemon-reload && sudo systemctl restart shop-api
grep -q '8000, 8080' /etc/nftables.conf
