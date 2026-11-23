# Wrong: sealing is switched off ("it slowed the batch down").
printf '[Journal]\nRateLimitBurst=3000\n' | sudo tee /etc/systemd/journald@audit.conf.d/40-quiet.conf > /dev/null
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf
sudo sed -i 's/^audit role\.chnage /audit role.change /' /etc/shop/audit.conf
sudo systemctl reload shop-audit
printf '[Journal]\nSeal=no\n' | sudo tee /etc/systemd/journald@audit.conf.d/70-fast.conf > /dev/null
sudo systemctl restart systemd-journald@audit
