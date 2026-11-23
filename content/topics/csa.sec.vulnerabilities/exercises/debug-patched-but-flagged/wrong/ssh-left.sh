# Wrong: two of the three. Both packages are patched and the scan is clean;
# port 22 still runs the old server program.
sudo apt-mark unhold rsync
sudo rm /etc/apt/preferences.d/deploy-tools
sudo apt-get update
sudo apt-get install -y --only-upgrade rsync git git-man
