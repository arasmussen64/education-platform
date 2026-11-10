# The finished user data. In the lab you'd fill the four gaps with nano;
# here it's written in one go, then launched.
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
lab-launch ~/user-data.yaml
