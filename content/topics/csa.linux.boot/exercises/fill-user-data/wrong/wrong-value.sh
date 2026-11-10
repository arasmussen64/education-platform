# Wrong: the tier is left as the placeholder instead of web, so the config
# line is SHOP_TIER=app.
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
      SHOP_TIER=app
runcmd:
  - mkdir -p /var/lib/shop
  - touch /var/lib/shop/ready
EOF
lab-launch ~/user-data.yaml
