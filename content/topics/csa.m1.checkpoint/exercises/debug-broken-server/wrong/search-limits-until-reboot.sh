# Wrong: shop-search was given limits that fit, but with set-property
# --runtime, which keeps them only until the next reboot. Then the unit's
# 128 MB and 5% come back, and so do the kills and the throttling.
sudo rm -f /srv/shop/export-2019.bin
sudo sed -i 's#^ExecStart=/usr/bin/shop-api#ExecStart=/usr/local/bin/shop-api#' /etc/systemd/system/shop-api.service
sudo systemctl daemon-reload; sudo systemctl restart shop-api
sudo chmod 700 /home/ben/.ssh
sudo sed -i 's/tcp dport 22 accept/tcp dport { 22, 8080 } accept/' /etc/nftables.conf
sudo nft -f /etc/nftables.conf
sudo systemctl disable --now shop-worker
sudo systemctl set-property --runtime shop-search MemoryMax=192M CPUQuota=40%
sudo systemctl restart shop-search || true
sleep 6
