# The reference run. "{ ...; } > FILE" writes everything the lines between
# the braces print into FILE.
mkdir -p ~/vuln

# 1. Scan both machines. pay1 has seven findings in five packages; batch-01,
# whose sudo is already patched and whose openssh is between its two fixes,
# has four.
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical
osv-scanner scan source --offline-vulnerabilities --offline -L dpkg-status:/srv/inventory/batch-01/dpkg-status --format vertical

# 2. The facts the policy asks for: is each CVE in KEV (and since when), can
# the attack be automated, is the impact total or partial; and each
# machine's exposure, owner and first-seen date.
grep -E 'CVE-2025-32463|CVE-2025-32462|CVE-2024-6387|CVE-2025-26465|CVE-2024-32487|CVE-2024-12084|CVE-2025-48384' /usr/share/lab-pay/kev-2026.11.10.csv /usr/share/lab-pay/ssvc.csv
cat /srv/inventory/assets.tsv /srv/vuln/first-seen.tsv /srv/vuln/policy.tsv

# 3. Patch pay1. Every finding there but one is due within 14 days, and that
# one is in sudo, which is patched anyway. Then restart the shop's own
# unit, which the rsync upgrade didn't restart, and look for anything else
# still running a replaced program.
sudo apt-get update
sudo apt-get install -y --only-upgrade sudo openssh-server openssh-client openssh-sftp-server less rsync git git-man
sudo lsof +L1
sudo systemctl restart shop-sync
sudo lsof +L1

# 4. The register. pay1 is exposed. sudo's CVE-2025-32463 and git's
# CVE-2025-48384 are in KEV with total impact: 3 days and forensic triage,
# counted from the day CISA listed them, which is long before the day the
# findings were first reported here. less and rsync are automatable with
# total impact: 3 days from 2026-11-16. openssh's two are 14 days, and
# sudo's CVE-2025-32462 (partial impact) 60. batch-01 is internal, and its
# clock starts on 2026-11-02: git's KEV entry 14 days from its listing,
# less and rsync 60 days, openssh's remaining one on the next upgrade.
{
  echo "CVE-2025-32463 pay1 sudo $(date -d '2025-09-29 + 3 days' +%F) yes fixed payments"
  echo "CVE-2025-32462 pay1 sudo $(date -d '2026-11-16 + 60 days' +%F) no fixed payments"
  echo "CVE-2024-6387 pay1 openssh $(date -d '2026-11-16 + 14 days' +%F) no fixed payments"
  echo "CVE-2025-26465 pay1 openssh $(date -d '2026-11-16 + 14 days' +%F) no fixed payments"
  echo "CVE-2024-32487 pay1 less $(date -d '2026-11-16 + 3 days' +%F) no fixed payments"
  echo "CVE-2024-12084 pay1 rsync $(date -d '2026-11-16 + 3 days' +%F) no fixed payments"
  echo "CVE-2025-48384 pay1 git $(date -d '2025-08-25 + 3 days' +%F) yes fixed payments"
  echo "CVE-2025-48384 batch-01 git $(date -d '2025-08-25 + 14 days' +%F) no open data-team"
  echo "CVE-2024-32487 batch-01 less $(date -d '2026-11-02 + 60 days' +%F) no open data-team"
  echo "CVE-2024-12084 batch-01 rsync $(date -d '2026-11-02 + 60 days' +%F) no open data-team"
  echo "CVE-2025-26465 batch-01 openssh on-upgrade no open data-team"
} > ~/vuln/register.tsv

# 5. This week's rescan, saved. A clean scan says "No issues found".
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical > ~/vuln/rescan.txt 2>&1
cat ~/vuln/rescan.txt
