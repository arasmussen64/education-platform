# Wrong: instead of finding why role changes are missing, the policy is
# replaced by one that records everything the shop does, noise included.
printf '[Journal]\nRateLimitBurst=3000\n' | sudo tee /etc/systemd/journald@audit.conf.d/40-quiet.conf > /dev/null
sudo rm /etc/systemd/journald@audit.conf.d/60-disk.conf
sudo tee /etc/shop/audit.conf > /dev/null << 'EOF'
audit login.ok user src outcome
audit login.failed user src outcome
audit page.view user src path
audit health.check user src path
audit role.change actor user old new src outcome
audit config.change actor setting old new src outcome
audit refund actor order amount src outcome
audit export actor table rows src outcome
audit card.update user card src outcome
mask card
EOF
sudo systemctl reload shop-audit
sudo systemctl restart systemd-journald@audit
