# Wrong: the rule for 8080 is added to the running firewall, but the file
# the firewall is loaded from at boot still says 8000, so the next reboot
# brings the ticket back.
sudo sed -i 's/^host-record=shop.internal,.*/host-record=shop.internal,10.0.9.1/' /etc/dnsmasq.d/shop.conf && sudo systemctl restart dnsmasq
sudo nft add rule inet filter input tcp dport 8080 accept
sudo mkdir -p /etc/systemd/system/shop-api.service.d && printf '[Service]\nEnvironment=BIND=0.0.0.0\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null && sudo systemctl daemon-reload && sudo systemctl restart shop-api
