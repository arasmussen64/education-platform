# Wrong: the pin edited to name today's fixed version (whichever the patch
# repository holds). The scan is clean today, and git is tied down again
# for every fix that comes after.
sudo apt-mark unhold rsync
sudo apt-get update
newest=$(apt-cache madison git | awk '{print $3}' | sort -V | tail -n 1)
sudo sed -i "s/^Pin: version .*/Pin: version $newest/" /etc/apt/preferences.d/deploy-tools
sudo apt-get install -y --only-upgrade rsync git git-man
sudo rm /etc/systemd/system/ssh.service.d/50-keep.conf
sudo systemctl daemon-reload
sudo systemctl restart ssh
