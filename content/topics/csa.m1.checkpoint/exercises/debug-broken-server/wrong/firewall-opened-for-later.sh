# Wrong: the API's port was opened, and the web's two ports, 80 and 443,
# with it, "in case the shop needs them later". Nobody asked for them, so
# from outside more than SSH and the API can be reached: anything that
# ever listens there is open to the world. Saved and loaded, so it lasts.
sudo rm -f /srv/shop/export-2019.bin
sudo sed -i 's#^ExecStart=/usr/bin/shop-api#ExecStart=/usr/local/bin/shop-api#' /etc/systemd/system/shop-api.service
sudo systemctl daemon-reload; sudo systemctl restart shop-api
sudo chmod 700 /home/ben/.ssh
sudo sed -i 's/tcp dport 22 accept/tcp dport { 22, 80, 443, 8080 } accept/' /etc/nftables.conf
sudo nft -f /etc/nftables.conf
sudo systemctl disable --now shop-worker
sudo mkdir -p /etc/systemd/system/shop-search.service.d
printf '[Service]\nMemoryMax=192M\nCPUQuota=40%%\n' | sudo tee /etc/systemd/system/shop-search.service.d/override.conf > /dev/null
sudo systemctl daemon-reload; sudo systemctl restart shop-search || true
sleep 6
