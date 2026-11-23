# The reference: three faults, each found from its own evidence.

# 1. The batch. After "shop-cli settle", the trail holds a few hundred of
# the 1,500 refunds, and half a minute later journald says why in the
# audit journal itself:
#   journalctl --namespace=audit | grep Suppressed
# A rate limit is dropping them. The settings in force, drop-ins included:
#   systemd-analyze cat-config systemd/journald@audit.conf
# show RateLimitBurst=50 in 40-quiet.conf. The limit stays, with room for
# two batches in half a minute. (printf ... | sudo tee FILE writes a file
# that only root may write.)
printf '[Journal]\nRateLimitBurst=3000\n' | sudo tee /etc/systemd/journald@audit.conf.d/40-quiet.conf > /dev/null

# 2. The reboot. The same listing shows Storage=volatile in 60-disk.conf:
# the trail's newest file is under /run, which is memory, and a journal in
# memory is never sealed either. Without the file the audit journal goes
# back to its disk.
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf

# 3. The role changes. The audit writer says what it can't use in the
# policy, as a warning in the audit journal:
#   journalctl --namespace=audit -u shop-audit -p warning
#   audit.conf line 8: no such event "role.chnage"
# One misspelt word. The writer reads the policy at a reload.
sudo sed -i 's/^audit role\.chnage /audit role.change /' /etc/shop/audit.conf
sudo systemctl reload shop-audit

# journald reads its settings when it starts.
sudo systemctl restart systemd-journald@audit
