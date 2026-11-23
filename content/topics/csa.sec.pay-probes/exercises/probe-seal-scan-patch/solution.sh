# The reference. "| sudo tee FILE > /dev/null" writes a line into a file
# that only root may write.

# 1. Sealing keys for the journal. The command's last line of output is the
# verification key, which goes to the auditors; the sealing key stays with
# journald. Then sealing on for the audit namespace, and its journald
# restarted so that it starts a sealed file.
sudo journalctl --setup-keys --interval=10s 2> /dev/null | tail -n 1 | sudo tee /srv/auditors/verify-key > /dev/null
sudo sed -i 's/^Seal=no$/Seal=yes/' /etc/systemd/journald@audit.conf
sudo systemctl restart systemd-journald@audit

# 2. Root can't log in over SSH: a drop-in, tested, and the server reloaded
# so that the running server has it too.
echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/60-hardening.conf > /dev/null
sudo sshd -t
sudo systemctl reload ssh

# 3. sudo, from the server's patch repository.
sudo apt-get update
sudo apt-get install -y --only-upgrade sudo
