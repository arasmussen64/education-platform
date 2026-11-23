# Wrong: two of the three faults fixed; the trail is still kept in memory.
printf '[Journal]\nRateLimitBurst=3000\n' | sudo tee /etc/systemd/journald@audit.conf.d/40-quiet.conf > /dev/null
sudo sed -i 's/^audit role\.chnage /audit role.change /' /etc/shop/audit.conf
sudo systemctl reload shop-audit
sudo systemctl restart systemd-journald@audit
