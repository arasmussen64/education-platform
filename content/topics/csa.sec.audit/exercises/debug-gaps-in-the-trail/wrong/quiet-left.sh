# Wrong: two of the three faults fixed; the batch still loses refunds.
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf
sudo sed -i 's/^audit role\.chnage /audit role.change /' /etc/shop/audit.conf
sudo systemctl reload shop-audit
sudo systemctl restart systemd-journald@audit
