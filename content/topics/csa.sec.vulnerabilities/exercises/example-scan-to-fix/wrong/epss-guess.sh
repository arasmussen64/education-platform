# Wrong: kev.txt made from EPSS, the scan's CVEs with a score above 0.5.
# A high probability is a prediction; KEV is a list of what has happened.
dpkg -l sudo openssh-server less rsync git | grep '^ii'
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical | grep -c UBUNTU-CVE
grep -h CVE-2025-32463 /usr/share/lab-pay/epss-2026-11-10.csv /usr/share/lab-pay/kev-2026.11.10.csv /usr/share/lab-pay/ssvc.csv
grep pay1 /srv/inventory/assets.tsv /srv/vuln/first-seen.tsv
awk -F'\t' '$1 == "yes" && $2 == "yes" && $3 == "no" && $4 == "total"' /srv/vuln/policy.tsv
date -d "2025-09-29 + 3 days" +%F
mkdir -p ~/example
cut -d, -f1 /usr/share/lab-pay/kev-2026.11.10.csv > ~/example/kev-ids.txt
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical | grep -o 'UBUNTU-CVE-[0-9]*-[0-9]*' | cut -d- -f2- | sort -u | while read -r cve; do awk -F, -v c="$cve" '$1 == c && $2 > 0.5 {print $1}' /usr/share/lab-pay/epss-2026-11-10.csv; done > ~/example/kev.txt
cat ~/example/kev.txt
echo "CVE-2025-32463 pay1 sudo 2025-10-02 yes open payments" > ~/example/register.tsv
echo "CVE-2025-32462 pay1 sudo $(date -d '2026-11-09 + 60 days' +%F) no open payments" >> ~/example/register.tsv
sudo apt-get update
sudo apt-get install -y --only-upgrade sudo rsync
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical | grep -c UBUNTU-CVE
sed -i 's/ open / fixed /' ~/example/register.tsv
cat ~/example/register.tsv
sudo lsof +L1
sudo systemctl restart shop-sync
sudo lsof +L1
nc -w 2 127.0.0.1 873 < /dev/null
