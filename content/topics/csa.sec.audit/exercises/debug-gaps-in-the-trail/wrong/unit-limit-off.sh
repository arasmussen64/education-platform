# Wrong: the journal's limit is left as it was, and the audit writer's own
# unit is given a drop-in that exempts it from any limit.
sudo mkdir -p /etc/systemd/system/shop-audit.service.d
printf '[Service]\nLogRateLimitIntervalSec=0\n' | sudo tee /etc/systemd/system/shop-audit.service.d/limit.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart shop-audit
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf
sudo sed -i 's/^audit role\.chnage /audit role.change /' /etc/shop/audit.conf
sudo systemctl reload shop-audit
sudo systemctl restart systemd-journald@audit
