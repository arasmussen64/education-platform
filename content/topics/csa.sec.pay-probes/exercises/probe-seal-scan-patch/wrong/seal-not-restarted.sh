# Wrong: keys made and Seal=yes written, but the audit namespace's journald
# was never restarted, so it still writes the unsealed file it had open.
sudo journalctl --setup-keys --interval=10s 2> /dev/null | tail -n 1 | sudo tee /srv/auditors/verify-key > /dev/null
sudo sed -i 's/^Seal=no$/Seal=yes/' /etc/systemd/journald@audit.conf
echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/60-hardening.conf > /dev/null
sudo sshd -t
sudo systemctl reload ssh
sudo apt-get update
sudo apt-get install -y --only-upgrade sudo
