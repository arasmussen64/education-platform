# The finished user data. In the lab you'd fill the four gaps with nano;
# here it's written in one go, then launched. The four values: the package,
# the file's path, the value in its content, and the one command.
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
  - touch /var/lib/shop/ready
EOF
lab-launch ~/user-data.yaml
