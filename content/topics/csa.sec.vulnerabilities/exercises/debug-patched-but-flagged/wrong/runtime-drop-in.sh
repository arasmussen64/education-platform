# Wrong: both packages patched, and the SSH server put right for today
# only. A second drop-in under /run, which a reboot empties, tells the unit
# to run the package's program; the one under /etc that runs the kept copy
# is still there, and is the only one left after the next boot.
sudo apt-mark unhold rsync
sudo rm /etc/apt/preferences.d/deploy-tools
sudo apt-get update
sudo apt-get install -y --only-upgrade rsync git git-man
sudo mkdir -p /run/systemd/system/ssh.service.d
printf '[Service]\nExecStart=\nExecStart=/usr/sbin/sshd -D $SSHD_OPTS\n' | sudo tee /run/systemd/system/ssh.service.d/zz-today.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart ssh
