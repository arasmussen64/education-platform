FROM lab-base-pay
# The payments server a week before its assessment. Two earlier jobs are
# already done on it, and the lab makes their end states here so that it
# stands alone:
#  - Audit logging's: the audit policy of seven events with the card
#    masked, the audit journal kept on disk for 400 days with room for 13
#    months, sealed, and the verification key left for the auditors (the
#    keys are made here, at build, so none is in the repository);
#  - Vulnerability management's: every package patched from the server's
#    own repository, the register and this week's rescan in ~/vuln, the
#    policy and the asset list, and shop-sync.service, the shop's own rsync
#    daemon that the bank fetches settlement files from (which is why rsync
#    can't be removed). The package's own rsync.service is masked: the
#    shop's unit is the only one meant to run.
# What is not done: root may log in over SSH (the hosting company's
# drop-in), nothing sets the password rules, and the server's own journal
# has no Storage= line. The lab adds the assessment's scope, the shop's
# collectors, and the checks' own copies and helpers.
COPY audit.conf /etc/shop/audit.conf
COPY journald@audit.conf /etc/systemd/journald@audit.conf
COPY rsyncd.conf /etc/shop/rsyncd.conf
COPY shop-sync.service /etc/systemd/system/shop-sync.service
COPY 05-hosting.conf /etc/ssh/sshd_config.d/05-hosting.conf
COPY scope.tsv collectors.tsv /srv/compliance/
COPY assets.tsv /srv/inventory/assets.tsv
COPY policy.tsv first-seen.tsv /srv/vuln/
COPY comply.sh pack-check scope.tsv collectors.tsv reference.tsv exception-rule audit.conf rsyncd.conf /usr/local/lib/lab-comp/
RUN cd /usr/local/lib/lab-comp \
 && chmod 755 pack-check \
 && chmod 644 comply.sh scope.tsv collectors.tsv reference.tsv exception-rule audit.conf rsyncd.conf \
      /etc/shop/audit.conf /etc/shop/rsyncd.conf /etc/systemd/journald@audit.conf /etc/systemd/system/shop-sync.service \
      /etc/ssh/sshd_config.d/05-hosting.conf /srv/compliance/* /srv/inventory/assets.tsv /srv/vuln/* \
 && ln -s /usr/local/lib/lab-pay/oscap-rules /usr/local/bin/oscap-rules \
 && mkdir -p /srv/settle /srv/auditors /run/sshd "/var/log/journal/$(cat /etc/machine-id)" \
 && journalctl --setup-keys --interval=10s 2> /dev/null > /srv/auditors/verify-key \
 && test -s /srv/auditors/verify-key \
 && apt-get update \
 && apt-get install -y --only-upgrade sudo openssh-server openssh-client openssh-sftp-server less rsync git git-man \
 && printf 'order,amount\nsettle-1,19.99\nsettle-2,5.00\n' > /srv/settle/settlement-2026-11-08.csv \
 && systemctl enable shop-sync.service \
 && systemctl mask rsync.service \
 && install -d -o learner -g learner /home/learner/vuln \
 && { echo "CVE-2025-32463 pay1 sudo $(date -d '2025-09-29 + 3 days' +%F) yes fixed payments" \
    ; echo "CVE-2025-32462 pay1 sudo $(date -d '2026-11-16 + 60 days' +%F) no fixed payments" \
    ; echo "CVE-2024-6387 pay1 openssh $(date -d '2026-11-16 + 14 days' +%F) no fixed payments" \
    ; echo "CVE-2025-26465 pay1 openssh $(date -d '2026-11-16 + 14 days' +%F) no fixed payments" \
    ; echo "CVE-2024-32487 pay1 less $(date -d '2026-11-16 + 3 days' +%F) no fixed payments" \
    ; echo "CVE-2024-12084 pay1 rsync $(date -d '2026-11-16 + 3 days' +%F) no fixed payments" \
    ; echo "CVE-2025-48384 pay1 git $(date -d '2025-08-25 + 3 days' +%F) yes fixed payments" \
    ; echo "CVE-2025-48384 batch-01 git $(date -d '2025-08-25 + 14 days' +%F) no open data-team" \
    ; echo "CVE-2024-32487 batch-01 less $(date -d '2026-11-02 + 60 days' +%F) no open data-team" \
    ; echo "CVE-2024-12084 batch-01 rsync $(date -d '2026-11-02 + 60 days' +%F) no open data-team" \
    ; echo "CVE-2025-26465 batch-01 openssh on-upgrade no open data-team" \
    ; } > /home/learner/vuln/register.tsv \
 && { osv-scanner scan source --offline-vulnerabilities --offline -L /var/lib/dpkg/status --format vertical > /home/learner/vuln/rescan.txt 2>&1 || true; } \
 && grep 'No issues found' /home/learner/vuln/rescan.txt > /dev/null \
 && chown learner:learner /home/learner/vuln/register.tsv /home/learner/vuln/rescan.txt \
 && sha256sum /srv/compliance/scope.tsv /srv/compliance/collectors.tsv /srv/inventory/assets.tsv /srv/vuln/policy.tsv /srv/vuln/first-seen.tsv > SHA256SUMS
