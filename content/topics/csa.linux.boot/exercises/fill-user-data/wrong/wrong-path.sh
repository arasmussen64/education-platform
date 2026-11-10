# Wrong: the file is written to /etc/shop/env instead of /etc/shop/report.env,
# so the config isn't where it belongs.
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
  - path: /etc/shop/env
    content: |
      SHOP_TIER=web
runcmd:
  - mkdir -p /var/lib/shop
  - touch /var/lib/shop/ready
EOF
lab-launch ~/user-data.yaml
