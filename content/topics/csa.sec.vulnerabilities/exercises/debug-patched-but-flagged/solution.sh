# The reference fix. Three things kept the patch run from finishing its job.

# 1. rsync was held, so the run kept it back (its log says so, and so does
# apt-mark showhold). Release the hold.
apt-mark showhold
sudo apt-mark unhold rsync

# 2. git was pinned to the version it had, with a priority above 1000, so
# apt saw nothing newer to install (apt-cache policy git shows the pin).
# Remove the pin.
apt-cache policy git
sudo rm /etc/apt/preferences.d/deploy-tools

# Now the patch repository's versions can be installed.
sudo apt-get update
sudo apt-get install -y --only-upgrade rsync git git-man

# 3. The SSH unit had a drop-in that ran a kept copy of the old server
# program instead of the package's, so the package was patched and port 22
# was not (systemctl cat ssh shows it). Remove the drop-in, have systemd
# read its unit files again, and restart the server.
systemctl cat ssh
sudo rm /etc/systemd/system/ssh.service.d/50-keep.conf
sudo systemctl daemon-reload
sudo systemctl restart ssh

# Prove it: a clean scan, and the new version on port 22.
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical
nc -w 2 127.0.0.1 22 < /dev/null
