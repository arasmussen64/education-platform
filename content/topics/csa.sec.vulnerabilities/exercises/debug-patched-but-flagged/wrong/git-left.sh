# Wrong: two of the three. rsync and the SSH server are put right; git is
# still tied to its old version and still flagged.
sudo apt-mark unhold rsync
sudo apt-get update
sudo apt-get install -y --only-upgrade rsync
sudo rm /etc/systemd/system/ssh.service.d/50-keep.conf
sudo systemctl daemon-reload
sudo systemctl restart ssh
