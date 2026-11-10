# Wrong: the name and the API are fixed, but the firewall still accepts
# port 8000, so the office's SYNs to 8080 are dropped.
sudo sed -i 's/^host-record=shop.internal,.*/host-record=shop.internal,10.0.9.1/' /etc/dnsmasq.d/shop.conf && sudo systemctl restart dnsmasq
sudo mkdir -p /etc/systemd/system/shop-api.service.d && printf '[Service]\nEnvironment=BIND=0.0.0.0\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null && sudo systemctl daemon-reload && sudo systemctl restart shop-api
