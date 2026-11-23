# Wrong: the kept copy of the SSH server replaced by a copy of today's.
# Port 22 announces the new version, and the next patch will leave the
# copy behind exactly as this one did.
sudo apt-mark unhold rsync
sudo rm /etc/apt/preferences.d/deploy-tools
sudo apt-get update
sudo apt-get install -y --only-upgrade rsync git git-man
sudo cp -p /usr/sbin/sshd /usr/local/sbin/sshd-stable
sudo systemctl restart ssh
