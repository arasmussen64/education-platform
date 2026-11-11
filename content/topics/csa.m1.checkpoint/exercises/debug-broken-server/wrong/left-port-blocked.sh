# Wrong: six faults fixed, but the firewall still has no rule for the API's
# port, so the API answers on the server and not from the office.
sudo rm -f /srv/shop/export-2019.bin
sudo sed -i 's#^ExecStart=/usr/bin/shop-api#ExecStart=/usr/local/bin/shop-api#' /etc/systemd/system/shop-api.service
sudo systemctl daemon-reload; sudo systemctl restart shop-api
sudo chmod 700 /home/ben/.ssh
sudo systemctl disable --now shop-worker
sudo mkdir -p /etc/systemd/system/shop-search.service.d
printf '[Service]\nMemoryMax=192M\nCPUQuota=40%%\n' | sudo tee /etc/systemd/system/shop-search.service.d/override.conf > /dev/null
sudo systemctl daemon-reload; sudo systemctl restart shop-search || true
sleep 6
