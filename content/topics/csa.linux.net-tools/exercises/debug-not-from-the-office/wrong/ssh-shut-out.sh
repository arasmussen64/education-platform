# Wrong: the name and the API are fixed, and the firewall's TCP rule is
# rewritten in a hurry for the API alone. The ticket is closed, and the
# office's administrators can no longer reach SSH: their connections to
# port 22 are dropped.
sudo sed -i 's/^host-record=shop.internal,.*/host-record=shop.internal,10.0.9.1/' /etc/dnsmasq.d/shop.conf && sudo systemctl restart dnsmasq
sudo sed -i 's/tcp dport { 22, 8000 } accept/tcp dport 8080 accept/' /etc/nftables.conf && sudo nft -f /etc/nftables.conf
sudo mkdir -p /etc/systemd/system/shop-api.service.d && printf '[Service]\nEnvironment=BIND=0.0.0.0\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null && sudo systemctl daemon-reload && sudo systemctl restart shop-api
grep -q 'tcp dport 8080 accept' /etc/nftables.conf
