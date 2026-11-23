# Wrong: rsync's finding cleared by removing rsync.
sudo apt-mark unhold rsync
sudo rm /etc/apt/preferences.d/deploy-tools
sudo apt-get update
sudo apt-get install -y --only-upgrade git git-man
sudo apt-get remove -y rsync
sudo rm /etc/systemd/system/ssh.service.d/50-keep.conf
sudo systemctl daemon-reload
sudo systemctl restart ssh
