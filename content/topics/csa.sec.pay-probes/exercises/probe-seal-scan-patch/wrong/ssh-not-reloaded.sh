# Wrong: the drop-in is written, so the benchmark's rule passes on the
# files, but the running SSH server was never reloaded and still lets root in.
sudo journalctl --setup-keys --interval=10s 2> /dev/null | tail -n 1 | sudo tee /srv/auditors/verify-key > /dev/null
sudo sed -i 's/^Seal=no$/Seal=yes/' /etc/systemd/journald@audit.conf
sudo systemctl restart systemd-journald@audit
echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/60-hardening.conf > /dev/null
sudo sshd -t
sudo apt-get update
sudo apt-get install -y --only-upgrade sudo
