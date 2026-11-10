# Wrong: the firewall and the API are fixed, but the office is still told
# shop.internal is 10.0.9.5, so by name it still reaches nobody.
sudo sed -i 's/{ 22, 8000 }/{ 22, 8080 }/' /etc/nftables.conf && sudo nft -f /etc/nftables.conf
sudo mkdir -p /etc/systemd/system/shop-api.service.d && printf '[Service]\nEnvironment=BIND=0.0.0.0\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null && sudo systemctl daemon-reload && sudo systemctl restart shop-api
