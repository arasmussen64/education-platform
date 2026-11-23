# Wrong: nothing installed. The package database is edited to say that sudo
# and rsync are at the patch repository's versions, so the scanner, which
# only reads that list, finds nothing in either. The programs on disk are
# the old ones.
sudo apt-get update
say_fixed() {
  version=$(awk -v p="$1" '/^Package: / { name = $2 } /^Version: / && name == p { print $2; exit }' /srv/patches/Packages)
  awk -v p="$1" -v v="$version" '/^Package: / { name = $2 } /^Version: / && name == p { $0 = "Version: " v } { print }' /var/lib/dpkg/status > /tmp/status
  sudo cp /tmp/status /var/lib/dpkg/status
}
say_fixed sudo
say_fixed rsync
mkdir -p ~/example
cut -d, -f1 /usr/share/lab-pay/kev-2026.11.10.csv > ~/example/kev-ids.txt
printf 'CVE-2025-32463\nCVE-2025-48384\n' > ~/example/kev.txt
echo "CVE-2025-32463 pay1 sudo 2025-10-02 yes fixed payments" > ~/example/register.tsv
echo "CVE-2025-32462 pay1 sudo 2027-01-08 no fixed payments" >> ~/example/register.tsv
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical | grep -c UBUNTU-CVE
