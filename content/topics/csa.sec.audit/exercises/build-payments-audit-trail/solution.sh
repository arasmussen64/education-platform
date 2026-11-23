# The reference. "sudo tee FILE > /dev/null << 'EOF'" writes the lines up to
# EOF into a file that only root may write (tee does the writing as root;
# its copy to the screen is thrown away).

# 1. The policy: the seven kinds of event an investigator will ask about,
# each with who, from where, what and how it ended; no page views or health
# checks; no password, session or token field on any line; and the card
# number masked to its last four digits. The writer reads it at a reload.
sudo tee /etc/shop/audit.conf > /dev/null << 'EOF'
# The payments server's audit policy.
audit login.ok user src outcome
audit login.failed user src outcome
audit role.change actor user old new src outcome
audit config.change actor setting old new src outcome
audit refund actor order amount src outcome
audit export actor table rows src outcome
audit card.update user card src outcome
mask card
EOF
sudo systemctl reload shop-audit

# 2. Sealing keys. Piped, the command prints only the verification key,
# which goes to the auditors; the sealing key stays with journald.
sudo journalctl --setup-keys --interval=10s 2> /dev/null | sudo tee /srv/auditors/verify-key > /dev/null

# 3. The audit journal's settings: on disk, sealed, deleted after 400 days
# (at least the 365 the card rules ask for, and no longer than the 400 the
# policy allows), with room for 13 months: 60,000 events x 300 bytes x 395
# days is 7.11 GB, more than journald's 4 GB default cap, so 8G. journald
# reads its settings when it starts.
sudo tee /etc/systemd/journald@audit.conf > /dev/null << 'EOF'
[Journal]
Storage=persistent
Seal=yes
MaxRetentionSec=400d
SystemMaxUse=8G
EOF
sudo systemctl restart systemd-journald@audit
