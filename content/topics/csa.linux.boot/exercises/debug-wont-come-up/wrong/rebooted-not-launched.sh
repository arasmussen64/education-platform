# Wrong: the user data is fixed, but the instance was only rebooted, not
# launched fresh, so the per-instance modules saw the same instance id and
# skipped everything; nothing got reconfigured.
cat > ~/user-data.yaml <<'EOF'
#cloud-config
users:
  - name: ben
    groups: sudo
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFakeKeyForTheLabOnly0000000000000000000000000 ben@laptop
packages:
  - shop-report
write_files:
  - path: /etc/shop/report.env
    content: |
      SHOP_TIER=web
runcmd:
  - mkdir -p /var/lib/shop
  - touch /var/lib/shop/ready
EOF
cp ~/user-data.yaml /var/lib/cloud/seed/nocloud/user-data 2>/dev/null || sudo cp ~/user-data.yaml /var/lib/cloud/seed/nocloud/user-data
lab-reboot
