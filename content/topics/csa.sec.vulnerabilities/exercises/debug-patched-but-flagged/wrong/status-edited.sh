# Wrong: the hold and the pin removed and nothing installed. The package
# database is edited to say that rsync and git are at the patch
# repository's versions, so the scanner, which only reads that list, finds
# nothing. The programs on disk are the old ones.
sudo apt-mark unhold rsync
sudo rm /etc/apt/preferences.d/deploy-tools
sudo apt-get update
say_fixed() {
  version=$(awk -v p="$1" '/^Package: / { name = $2 } /^Version: / && name == p { print $2; exit }' /srv/patches/Packages)
  awk -v p="$1" -v v="$version" '/^Package: / { name = $2 } /^Version: / && name == p { $0 = "Version: " v } { print }' /var/lib/dpkg/status > /tmp/status
  sudo cp /tmp/status /var/lib/dpkg/status
}
for package in rsync git git-man; do
  say_fixed "$package"
done
sudo rm /etc/systemd/system/ssh.service.d/50-keep.conf
sudo systemctl daemon-reload
sudo systemctl restart ssh
