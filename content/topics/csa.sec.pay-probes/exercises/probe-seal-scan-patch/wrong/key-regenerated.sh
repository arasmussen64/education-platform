# Wrong: the key was handed over, and then the keys were made again ("to be
# sure") and journald restarted: the trail is sealed with keys the auditors'
# key no longer matches.
sudo journalctl --setup-keys --interval=10s 2> /dev/null | tail -n 1 | sudo tee /srv/auditors/verify-key > /dev/null
sudo sed -i 's/^Seal=no$/Seal=yes/' /etc/systemd/journald@audit.conf
sudo systemctl restart systemd-journald@audit
sudo journalctl --setup-keys --force --interval=10s > /dev/null 2>&1
sudo systemctl restart systemd-journald@audit
echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/60-hardening.conf > /dev/null
sudo sshd -t
sudo systemctl reload ssh
sudo apt-get update
sudo apt-get install -y --only-upgrade sudo
