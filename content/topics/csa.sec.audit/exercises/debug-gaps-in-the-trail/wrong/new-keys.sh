# Wrong: sealing looked broken, so new keys were made, and the auditors
# still hold the old verification key.
printf '[Journal]\nRateLimitBurst=3000\n' | sudo tee /etc/systemd/journald@audit.conf.d/40-quiet.conf > /dev/null
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf
sudo sed -i 's/^audit role\.chnage /audit role.change /' /etc/shop/audit.conf
sudo systemctl reload shop-audit
sudo journalctl --setup-keys --force --interval=10s > /dev/null 2>&1
sudo systemctl restart systemd-journald@audit
