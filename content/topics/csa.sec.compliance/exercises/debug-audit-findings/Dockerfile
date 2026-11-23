FROM lab-base-pay
# The payments server a month after its evidence pack was made. The first
# half of this file is the same server as "The payments server's evidence
# pack" (Audit logging's and Vulnerability management's end states, made
# here so that the lab stands alone; the sealing keys are made at build, so
# none is in the repository). Then that lab's fixes are applied, the pack
# is laid down as it was handed over last month, with an exception that
# still has months to run, and the story's three faults go in: two things
# that changed on the server since, and one line of the pack that was never
# right.
COPY audit.conf /etc/shop/audit.conf
COPY journald@audit.conf /etc/systemd/journald@audit.conf
COPY rsyncd.conf /etc/shop/rsyncd.conf
COPY shop-sync.service /etc/systemd/system/shop-sync.service
COPY scope.tsv collectors.tsv /srv/compliance/
COPY assets.tsv /srv/inventory/assets.tsv
COPY policy.tsv first-seen.tsv /srv/vuln/
COPY comply.sh pack-check scope.tsv collectors.tsv reference.tsv exception-rule audit.conf rsyncd.conf /usr/local/lib/lab-comp/
COPY pack.tsv rules.txt /home/learner/evidence/
COPY 20-support.conf /etc/systemd/system/ssh.service.d/20-support.conf
COPY 60-disk.conf 90-wear.conf /etc/systemd/journald.conf.d/
RUN cd /usr/local/lib/lab-comp \
 && chmod 755 pack-check \
 && chmod 644 comply.sh scope.tsv collectors.tsv reference.tsv exception-rule audit.conf rsyncd.conf \
      /etc/shop/audit.conf /etc/shop/rsyncd.conf /etc/systemd/journald@audit.conf /etc/systemd/system/shop-sync.service \
      /srv/compliance/* /srv/inventory/assets.tsv /srv/vuln/* \
      /etc/systemd/system/ssh.service.d/20-support.conf /etc/systemd/journald.conf.d/60-disk.conf /etc/systemd/journald.conf.d/90-wear.conf \
 && ln -s /usr/local/lib/lab-pay/oscap-rules /usr/local/bin/oscap-rules \
 && ln -s /usr/local/lib/lab-pay/root-login /usr/local/bin/root-login \
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
 && sha256sum /srv/compliance/scope.tsv /srv/compliance/collectors.tsv /srv/inventory/assets.tsv /srv/vuln/policy.tsv /srv/vuln/first-seen.tsv > SHA256SUMS \
 # Last month's fixes: root's login switched off in SSH's files, and the
 # password settings (the shop also limits repeated characters).
 && echo 'PermitRootLogin no' > /etc/ssh/sshd_config.d/60-hardening.conf \
 && printf 'minlen = 14\ndcredit = -1\nlcredit = -1\nmaxrepeat = 3\n' >> /etc/security/pwquality.conf \
 # Last month's pack: the collectors' outputs as they were then (and are
 # now), and the exception, which runs for another 200 days.
 && cd /home/learner/evidence \
 && cat /etc/shop/audit.conf > audit-policy.txt \
 && { echo '# /etc/systemd/journald@audit.conf'; cat /etc/systemd/journald@audit.conf; } > audit-retention.txt \
 && cp /home/learner/vuln/rescan.txt vuln-rescan.txt \
 && cp /home/learner/vuln/register.tsv vuln-register.txt \
 && { echo 'control: cis-ubuntu-24.04 2.1.13' \
    ; echo 'rule: package_rsync_removed' \
    ; echo "reason: the bank's server fetches each night's settlement file from this server's rsync daemon" \
    ; echo "compensating-control: the share is read-only and answers only the bank's address, 198.51.100.7" \
    ; echo 'owner: payments' \
    ; echo "expires: $(date -d '+200 days' +%F)" \
    ; } > exception.txt \
 && chown -R learner:learner /home/learner/evidence /home/learner/vuln
