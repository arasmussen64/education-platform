# Wrong: the journal's settings are overridden under /run, which works
# until the next reboot empties /run and last week's files apply again.
sudo mkdir -p /run/systemd/journald@audit.conf.d
printf '[Journal]\nRateLimitBurst=3000\nStorage=persistent\n' | sudo tee /run/systemd/journald@audit.conf.d/99-now.conf > /dev/null
sudo sed -i 's/^audit role\.chnage /audit role.change /' /etc/shop/audit.conf
sudo systemctl reload shop-audit
sudo systemctl restart systemd-journald@audit
