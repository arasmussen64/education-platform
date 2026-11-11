# Wrong: sshd was told to stop checking permissions (StrictModes no) and
# reloaded, and then the setting was deleted again without a reload. The
# files look right, but the server that is running still has the loose
# setting, and that is the only reason Ben's key works: his ~/.ssh is as
# it was, and the next restart of sshd locks him out again.
sudo rm -f /srv/shop/export-2019.bin
sudo sed -i 's#^ExecStart=/usr/bin/shop-api#ExecStart=/usr/local/bin/shop-api#' /etc/systemd/system/shop-api.service
sudo systemctl daemon-reload; sudo systemctl restart shop-api
printf 'StrictModes no\n' | sudo tee /etc/ssh/sshd_config.d/99-strictmodes.conf > /dev/null
sudo systemctl reload ssh || sudo systemctl restart ssh
sleep 2
sudo rm /etc/ssh/sshd_config.d/99-strictmodes.conf
sudo sed -i 's/tcp dport 22 accept/tcp dport { 22, 8080 } accept/' /etc/nftables.conf
sudo nft -f /etc/nftables.conf
sudo systemctl disable --now shop-worker
sudo mkdir -p /etc/systemd/system/shop-search.service.d
printf '[Service]\nMemoryMax=192M\nCPUQuota=40%%\n' | sudo tee /etc/systemd/system/shop-search.service.d/override.conf > /dev/null
sudo systemctl daemon-reload; sudo systemctl restart shop-search || true
sleep 6
