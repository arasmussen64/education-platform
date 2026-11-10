# Wrong: the package and the path are fixed, but the marker is still written
# into a directory that doesn't exist, so runcmd fails and cloud-init ends
# degraded.
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
  - touch /var/lib/shop-data/ready
EOF
lab-launch ~/user-data.yaml
