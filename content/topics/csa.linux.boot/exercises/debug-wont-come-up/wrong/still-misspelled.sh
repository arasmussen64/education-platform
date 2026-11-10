# Wrong: the path and the marker are fixed, but the package name is still
# misspelled, so shop-report isn't installed and cloud-init still errors.
cat > ~/user-data.yaml <<'EOF'
#cloud-config
users:
  - name: ben
    groups: sudo
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFakeKeyForTheLabOnly0000000000000000000000000 ben@laptop
packages:
  - shop-reprot
write_files:
  - path: /etc/shop/report.env
    content: |
      SHOP_TIER=web
runcmd:
  - mkdir -p /var/lib/shop
  - touch /var/lib/shop/ready
EOF
lab-launch ~/user-data.yaml
