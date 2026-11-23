# Wrong: the server told to stop announcing its package version, which
# hides the evidence, changes SSH's settings and leaves the old program
# running.
sudo apt-mark unhold rsync
sudo rm /etc/apt/preferences.d/deploy-tools
sudo apt-get update
sudo apt-get install -y --only-upgrade rsync git git-man
echo 'DebianBanner no' | sudo tee /etc/ssh/sshd_config.d/50-quiet.conf > /dev/null
sudo systemctl restart ssh
