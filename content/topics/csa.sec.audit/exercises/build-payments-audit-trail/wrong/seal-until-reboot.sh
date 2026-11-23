# Wrong: the settings file still says Seal=no, and sealing is switched on
# by a drop-in under /run, which a reboot empties: the trail is sealed
# today and unsealed after the next restart.
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
sudo journalctl --setup-keys --interval=10s 2> /dev/null | sudo tee /srv/auditors/verify-key > /dev/null
sudo tee /etc/systemd/journald@audit.conf > /dev/null << 'EOF'
[Journal]
Storage=persistent
Seal=no
MaxRetentionSec=400d
SystemMaxUse=8G
EOF
sudo mkdir -p /run/systemd/journald@audit.conf.d
printf '[Journal]\nSeal=yes\n' | sudo tee /run/systemd/journald@audit.conf.d/99-now.conf > /dev/null
sudo systemctl restart systemd-journald@audit
