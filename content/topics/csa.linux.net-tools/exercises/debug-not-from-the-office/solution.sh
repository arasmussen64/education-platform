# The three fixes, one per layer. In the lab you'd use nano; here sed and a
# drop-in do the editing.
# 1. The name: shop.internal pointed at 10.0.9.5, an address this server
#    doesn't have, so the office's packets went to nobody.
sudo sed -i 's/^host-record=shop.internal,.*/host-record=shop.internal,10.0.9.1/' /etc/dnsmasq.d/shop.conf && sudo systemctl restart dnsmasq
# 2. The firewall accepted the API's old port, 8000, so the office's SYNs to
#    8080 were dropped: no answer at all.
sudo sed -i 's/{ 22, 8000 }/{ 22, 8080 }/' /etc/nftables.conf && sudo nft -f /etc/nftables.conf
# 3. The API was bound to 127.0.0.1, so once the firewall let the office in,
#    its connection was refused. A drop-in overrides the unit's setting.
sudo mkdir -p /etc/systemd/system/shop-api.service.d && printf '[Service]\nEnvironment=BIND=0.0.0.0\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null && sudo systemctl daemon-reload && sudo systemctl restart shop-api
sleep 1; from-office dig +short shop.internal; sudo ss -ltn sport = :8080; from-office curl -s http://shop.internal:8080/
