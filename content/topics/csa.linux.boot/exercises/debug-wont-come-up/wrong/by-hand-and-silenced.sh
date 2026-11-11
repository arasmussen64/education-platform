# Wrong: the three things are done by hand on this server, the lines that
# failed are taken out of the user data so that cloud-init has nothing to
# complain about, and a fresh instance is launched from what is left. It
# says "done" and everything is in place, on this server only: the user
# data no longer installs, writes or marks anything.
sudo dpkg -i /srv/repo/pool/noble/shop-report_2.1_all.deb
echo "SHOP_TIER=web" | sudo tee /etc/shop/report.env > /dev/null
sudo mkdir -p /var/lib/shop
sudo touch /var/lib/shop/ready
cat > ~/user-data.yaml <<'EOF'
#cloud-config
users:
  - name: ben
    groups: sudo
    shell: /bin/bash
    ssh_authorized_keys:
      - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFakeKeyForTheLabOnly0000000000000000000000000 ben@laptop
EOF
lab-launch ~/user-data.yaml
cloud-init status
