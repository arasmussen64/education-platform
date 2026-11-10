# Wrong: four faults fixed, but the firewall was never given a rule for the
# API's port, so 8080 is still blocked from outside.
sudo rm -f /srv/shop/old.bin
sudo sed -i 's#/usr/local/bin/shop-api-typo#/usr/local/bin/shop-api#' /etc/systemd/system/shop-api.service
sudo systemctl daemon-reload; sudo systemctl restart shop-api
sudo chmod 700 /home/ben/.ssh
sudo systemctl disable --now shop-worker
