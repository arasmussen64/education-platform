# Wrong: the package and the settings path are fixed, and the failing
# command is made to succeed by creating the folder it names. cloud-init
# finishes without errors, and the marker is at /var/lib/shop-data/ready,
# where nothing looks for it; the load balancer still waits.
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
  - mkdir -p /var/lib/shop-data
  - touch /var/lib/shop-data/ready
EOF
lab-launch ~/user-data.yaml
cloud-init status
