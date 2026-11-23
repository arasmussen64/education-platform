# Wrong: two of the three faults fixed; role changes are still not recorded.
printf '[Journal]\nRateLimitBurst=3000\n' | sudo tee /etc/systemd/journald@audit.conf.d/40-quiet.conf > /dev/null
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf
sudo systemctl restart systemd-journald@audit
