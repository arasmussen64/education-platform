# Wrong: the policy file is right, but the audit writer was never told to
# read it again, so it still records sign-ins only.
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
sudo journalctl --setup-keys --interval=10s 2> /dev/null | sudo tee /srv/auditors/verify-key > /dev/null
sudo tee /etc/systemd/journald@audit.conf > /dev/null << 'EOF'
[Journal]
Storage=persistent
Seal=yes
MaxRetentionSec=400d
SystemMaxUse=8G
EOF
sudo systemctl restart systemd-journald@audit
