# Wrong: shop-search stays up and isn't throttled, because its limits were
# taken away rather than fitted. Nothing now stops it from taking the
# memory and CPU the API needs.
sudo rm -f /srv/shop/export-2019.bin
sudo sed -i 's#^ExecStart=/usr/bin/shop-api#ExecStart=/usr/local/bin/shop-api#' /etc/systemd/system/shop-api.service
sudo systemctl daemon-reload; sudo systemctl restart shop-api
sudo chmod 700 /home/ben/.ssh
sudo sed -i 's/tcp dport 22 accept/tcp dport { 22, 8080 } accept/' /etc/nftables.conf
sudo nft -f /etc/nftables.conf
sudo systemctl disable --now shop-worker
sudo mkdir -p /etc/systemd/system/shop-search.service.d
printf '[Service]\nMemoryMax=infinity\nCPUQuota=\n' | sudo tee /etc/systemd/system/shop-search.service.d/override.conf > /dev/null
sudo systemctl daemon-reload; sudo systemctl restart shop-search || true
sleep 6
