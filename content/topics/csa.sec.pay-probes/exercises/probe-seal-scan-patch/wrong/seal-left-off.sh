# Wrong: keys made and handed over, but sealing was never switched on for
# the audit namespace.
sudo journalctl --setup-keys --interval=10s 2> /dev/null | tail -n 1 | sudo tee /srv/auditors/verify-key > /dev/null
sudo systemctl restart systemd-journald@audit
echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/60-hardening.conf > /dev/null
sudo sshd -t
sudo systemctl reload ssh
sudo apt-get update
sudo apt-get install -y --only-upgrade sudo
