# Wrong: root's authorised keys were emptied instead of the setting being
# changed: no key gets in today, but root logins are still allowed.
sudo journalctl --setup-keys --interval=10s 2> /dev/null | tail -n 1 | sudo tee /srv/auditors/verify-key > /dev/null
sudo sed -i 's/^Seal=no$/Seal=yes/' /etc/systemd/journald@audit.conf
sudo systemctl restart systemd-journald@audit
sudo truncate -s 0 /root/.ssh/authorized_keys
sudo apt-get update
sudo apt-get install -y --only-upgrade sudo
