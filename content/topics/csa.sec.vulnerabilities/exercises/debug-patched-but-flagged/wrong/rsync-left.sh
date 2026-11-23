# Wrong: two of the three. git and the SSH server are put right; rsync is
# still held back and still flagged.
sudo rm /etc/apt/preferences.d/deploy-tools
sudo apt-get update
sudo apt-get install -y --only-upgrade git git-man
sudo rm /etc/systemd/system/ssh.service.d/50-keep.conf
sudo systemctl daemon-reload
sudo systemctl restart ssh
