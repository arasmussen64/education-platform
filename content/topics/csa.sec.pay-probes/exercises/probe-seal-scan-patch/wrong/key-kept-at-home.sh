# Wrong: the verification key was saved in the admin's own home folder and
# never handed to the auditors.
sudo journalctl --setup-keys --interval=10s 2> /dev/null | tail -n 1 | tee ~/verify-key > /dev/null
sudo sed -i 's/^Seal=no$/Seal=yes/' /etc/systemd/journald@audit.conf
sudo systemctl restart systemd-journald@audit
echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/60-hardening.conf > /dev/null
sudo sshd -t
sudo systemctl reload ssh
sudo apt-get update
sudo apt-get install -y --only-upgrade sudo
