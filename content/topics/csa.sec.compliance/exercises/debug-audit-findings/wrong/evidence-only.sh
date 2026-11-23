# The pack is corrected and collected again, and the server is left as
# it is.

# 3. The pack. Compare each control's rule lines with the crosswalk. For
# PCI DSS 8.3.6 the crosswalk has three rules, and the pack has two of them
# and one that is mapped to other controls: maxrepeat, where minlen should
# be.
awk -F'\t' '$2 == "pci-dss-4.0" && $3 == "8.3.6" { print $1 }' /usr/share/lab-pay/refs.tsv
grep 8.3.6 ~/evidence/pack.tsv
awk -F'\t' '$1 == "accounts_password_pam_maxrepeat" && $2 == "pci-dss-4.0"' /usr/share/lab-pay/refs.tsv
sed -i 's/accounts_password_pam_maxrepeat/accounts_password_pam_minlen/' ~/evidence/pack.tsv

# 4. Collect again, after the last fix: the pack's seven rules, and the
# collectors (theirs haven't changed, and are saved again so that the whole
# pack is of one day).
sudo oscap-rules sshd_disable_root_login accounts_password_pam_minlen accounts_password_pam_dcredit accounts_password_pam_lcredit journald_storage package_rsync_removed service_rsyncd_disabled > ~/evidence/rules.txt
cat ~/evidence/rules.txt
cat /etc/shop/audit.conf > ~/evidence/audit-policy.txt
systemd-analyze cat-config systemd/journald@audit.conf > ~/evidence/audit-retention.txt
osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical > ~/evidence/vuln-rescan.txt 2>&1
cat /home/learner/vuln/register.tsv > ~/evidence/vuln-register.txt
