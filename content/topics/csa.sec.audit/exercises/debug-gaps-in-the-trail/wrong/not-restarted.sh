# Wrong: every file is right, but the audit journal was never restarted,
# so it still runs with last week's settings.
printf '[Journal]\nRateLimitBurst=3000\n' | sudo tee /etc/systemd/journald@audit.conf.d/40-quiet.conf > /dev/null
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf
sudo sed -i 's/^audit role\.chnage /audit role.change /' /etc/shop/audit.conf
sudo systemctl reload shop-audit
