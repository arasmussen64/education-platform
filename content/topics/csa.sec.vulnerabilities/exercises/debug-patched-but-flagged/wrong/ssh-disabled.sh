# Wrong: the old version made to go away from port 22 by switching SSH
# off. Nobody can log in.
sudo apt-mark unhold rsync
sudo rm /etc/apt/preferences.d/deploy-tools
sudo apt-get update
sudo apt-get install -y --only-upgrade rsync git git-man
sudo systemctl disable --now ssh || true
sudo systemctl stop ssh.socket || true
