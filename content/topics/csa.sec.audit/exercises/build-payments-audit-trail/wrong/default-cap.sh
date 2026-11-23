# Wrong: no size set, so journald's default cap of 4 GB applies and the
# oldest months are deleted to make room long before the year is up.
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
Seal=yes
MaxRetentionSec=400d
EOF
sudo systemctl restart systemd-journald@audit
