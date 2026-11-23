# Wrong: sealing looked broken, so new keys were made and the new
# verification key was written over the auditors' copy. The trail seals
# again from today, and the year of history sealed with the old keys can no
# longer be checked by anyone. (The first file after new keys doesn't
# verify on this systemd, so the journal is restarted once more.)
printf '[Journal]\nRateLimitBurst=3000\n' | sudo tee /etc/systemd/journald@audit.conf.d/40-quiet.conf > /dev/null
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf
sudo sed -i 's/^audit role\.chnage /audit role.change /' /etc/shop/audit.conf
sudo systemctl reload shop-audit
sudo journalctl --setup-keys --force --interval=10s 2> /dev/null | sudo tee /srv/auditors/verify-key > /dev/null
sudo systemctl restart systemd-journald@audit
sleep 2
sudo systemctl restart systemd-journald@audit
