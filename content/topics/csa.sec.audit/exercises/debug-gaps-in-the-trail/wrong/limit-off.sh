# Wrong: the batch gets through because the rate limit is switched off
# altogether, so one runaway service can fill the audit journal.
printf '[Journal]\nRateLimitIntervalSec=0\n' | sudo tee /etc/systemd/journald@audit.conf.d/40-quiet.conf > /dev/null
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf
sudo sed -i 's/^audit role\.chnage /audit role.change /' /etc/shop/audit.conf
sudo systemctl reload shop-audit
sudo systemctl restart systemd-journald@audit
