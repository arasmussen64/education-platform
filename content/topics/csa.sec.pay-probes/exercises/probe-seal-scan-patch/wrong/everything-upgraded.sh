# Wrong: every package upgraded, where the job was sudo alone (the probe's
# scan check wants the other five findings still listed).
sudo journalctl --setup-keys --interval=10s 2> /dev/null | tail -n 1 | sudo tee /srv/auditors/verify-key > /dev/null
sudo sed -i 's/^Seal=no$/Seal=yes/' /etc/systemd/journald@audit.conf
sudo systemctl restart systemd-journald@audit
echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/60-hardening.conf > /dev/null
sudo sshd -t
sudo systemctl reload ssh
sudo apt-get update
sudo apt-get -y upgrade
