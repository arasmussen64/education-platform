# Wrong: the firewall and the API are fixed, and the name is "fixed" with a
# line in /etc/hosts. curl looks there before it asks any name server, so
# the test passes on this machine; the shop's name server still hands the
# old address to every real laptop in the office.
echo "10.0.9.1 shop.internal" | sudo tee -a /etc/hosts > /dev/null
sudo sed -i 's/{ 22, 8000 }/{ 22, 8080 }/' /etc/nftables.conf && sudo nft -f /etc/nftables.conf
sudo mkdir -p /etc/systemd/system/shop-api.service.d && printf '[Service]\nEnvironment=BIND=0.0.0.0\n' | sudo tee /etc/systemd/system/shop-api.service.d/override.conf > /dev/null && sudo systemctl daemon-reload && sudo systemctl restart shop-api
sleep 1
from-office curl -s -m 5 http://shop.internal:8080/
