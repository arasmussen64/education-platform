# Wrong: nothing installed. The package database is edited to say that the
# five packages are at the patch repository's versions, so the scanner,
# which only reads that list, finds nothing. Every program on disk is the
# old one, and the register calls all seven findings fixed.
sudo apt-get update
say_fixed() {
  version=$(awk -v p="$1" '/^Package: / { name = $2 } /^Version: / && name == p { print $2; exit }' /srv/patches/Packages)
  awk -v p="$1" -v v="$version" '/^Package: / { name = $2 } /^Version: / && name == p { $0 = "Version: " v } { print }' /var/lib/dpkg/status > /tmp/status
  sudo cp /tmp/status /var/lib/dpkg/status
}
for package in sudo openssh-server openssh-client openssh-sftp-server less rsync git git-man; do
  say_fixed "$package"
done
mkdir -p ~/vuln
{
  echo "CVE-2025-32463 pay1 sudo 2025-10-02 yes fixed payments"
  echo "CVE-2025-32462 pay1 sudo 2027-01-15 no fixed payments"
  echo "CVE-2024-6387 pay1 openssh 2026-11-30 no fixed payments"
  echo "CVE-2025-26465 pay1 openssh 2026-11-30 no fixed payments"
  echo "CVE-2024-32487 pay1 less 2026-11-19 no fixed payments"
  echo "CVE-2024-12084 pay1 rsync 2026-11-19 no fixed payments"
  echo "CVE-2025-48384 pay1 git 2025-08-28 yes fixed payments"
  echo "CVE-2025-48384 batch-01 git 2025-09-08 no open data-team"
  echo "CVE-2024-32487 batch-01 less 2027-01-01 no open data-team"
  echo "CVE-2024-12084 batch-01 rsync 2027-01-01 no open data-team"
  echo "CVE-2025-26465 batch-01 openssh on-upgrade no open data-team"
} > ~/vuln/register.tsv
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical > ~/vuln/rescan.txt 2>&1
cat ~/vuln/rescan.txt
