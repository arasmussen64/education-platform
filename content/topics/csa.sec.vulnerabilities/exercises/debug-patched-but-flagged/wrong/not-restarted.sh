# Wrong: the drop-in removed and systemd told, but the server never
# restarted: the old program is still the one answering on port 22, until
# the next reboot.
sudo apt-mark unhold rsync
sudo rm /etc/apt/preferences.d/deploy-tools
sudo apt-get update
sudo apt-get install -y --only-upgrade rsync git git-man
sudo rm /etc/systemd/system/ssh.service.d/50-keep.conf
sudo systemctl daemon-reload
