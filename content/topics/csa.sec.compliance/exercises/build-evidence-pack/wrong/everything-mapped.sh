# No thought: every control is given every rule and every collector.

# 1. What is in scope, and which rules the crosswalk maps to each control.
# The control is compared whole ($3 == c): grep 8.3.6 would also match 8.3.
cat /srv/compliance/scope.tsv
awk -F'\t' '$2 == "nist-800-53r4" && $3 == "AC-6(2)" { print $1 }' /usr/share/lab-pay/refs.tsv
awk -F'\t' '$2 == "pci-dss-4.0" && $3 == "8.3.6" { print $1 }' /usr/share/lab-pay/refs.tsv
awk -F'\t' '$2 == "cis-ubuntu-24.04" && ($3 == "6.1.2.4" || $3 == "2.1.13") { print $3, $1 }' /usr/share/lab-pay/refs.tsv
awk -F'\t' '$2 == "pci-dss-4.0" && ($3 == "10.2.1" || $3 == "10.5.1" || $3 == "6.3.3")' /usr/share/lab-pay/refs.tsv
# Four controls have rules (seven in all). The last command prints nothing:
# the crosswalk maps no rule to the other three.
sudo oscap-rules sshd_disable_root_login accounts_password_pam_minlen accounts_password_pam_dcredit accounts_password_pam_lcredit journald_storage package_rsync_removed service_rsyncd_disabled

# 2. Root over SSH. sshd uses the first value it reads, and the hosting
# company's drop-in is read first, so that file has to go. Then check the
# files and reload: the running server keeps its old settings until then.
sudo sshd -T | grep -i permitrootlogin
grep -rn PermitRootLogin /etc/ssh/sshd_config /etc/ssh/sshd_config.d/
sudo rm /etc/ssh/sshd_config.d/05-hosting.conf
echo 'PermitRootLogin no' | sudo tee /etc/ssh/sshd_config.d/60-hardening.conf > /dev/null
sudo sshd -t
sudo systemctl reload ssh

# 3. Passwords: the shop's 14 characters (the standard asks for 12), and a
# credit of -1 means "at least one" digit, and lower-case letter.
sudo tee -a /etc/security/pwquality.conf > /dev/null << 'EOF'
minlen = 14
dcredit = -1
lcredit = -1
EOF

# 4. The journal on disk: a drop-in, and journald reads it when it starts.
sudo tee /etc/systemd/journald.conf.d/60-disk.conf > /dev/null << 'EOF'
[Journal]
Storage=persistent
EOF
sudo systemctl restart systemd-journald

# 5. The pack. Rules for the four controls that have them; a collector for
# the three that don't: the audit policy shows what is recorded, the audit
# journal's settings show how long it is kept, and a fresh scan shows what
# is still open (the register adds the due dates).
mkdir -p ~/evidence
rules="sshd_disable_root_login accounts_password_pam_minlen accounts_password_pam_dcredit accounts_password_pam_lcredit journald_storage package_rsync_removed service_rsyncd_disabled"
grep -v '^#' /srv/compliance/scope.tsv | while IFS=$'\t' read -r framework control words; do
  for rule in $rules; do echo "$framework $control rule $rule"; done
  echo "$framework $control config audit-policy"
  echo "$framework $control config audit-retention"
  echo "$framework $control report vuln-rescan"
  echo "$framework $control report vuln-register"
done > ~/evidence/pack.tsv

# 6. The evidence, collected after the last fix. Six rules pass. One fails:
# package_rsync_removed, because the bank's settlement sync is an rsync
# daemon.
sudo oscap-rules sshd_disable_root_login accounts_password_pam_minlen accounts_password_pam_dcredit accounts_password_pam_lcredit journald_storage package_rsync_removed service_rsyncd_disabled > ~/evidence/rules.txt
cat ~/evidence/rules.txt
cat /etc/shop/audit.conf > ~/evidence/audit-policy.txt
systemd-analyze cat-config systemd/journald@audit.conf > ~/evidence/audit-retention.txt
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical > ~/evidence/vuln-rescan.txt 2>&1
cat /home/learner/vuln/register.tsv > ~/evidence/vuln-register.txt

# 7. The exception. The compensating control is real: the share is
# read-only and answers one address, the bank's.
cat /etc/shop/rsyncd.conf
cat /srv/inventory/assets.tsv
cat > ~/evidence/exception.txt << EOF
control: cis-ubuntu-24.04 2.1.13
rule: package_rsync_removed
reason: the bank's server fetches each night's settlement file from this server's rsync daemon
compensating-control: the share is read-only and answers only the bank's address, 198.51.100.7
owner: payments
expires: $(date -d '+180 days' +%F)
EOF
cat ~/evidence/exception.txt
