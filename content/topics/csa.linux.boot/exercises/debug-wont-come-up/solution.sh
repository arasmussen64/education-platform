# The three faults were all in the user data:
# 1. The package name was misspelled (shop-reprot), so apt couldn't find it.
#    cloud-init status --long and the output log both name it.
# 2. write_files put the settings at /etc/shop/report.conf; the tool reads
#    /etc/shop/report.env. Nothing errors for this one: it shows only when
#    the file is compared with what it is meant to do.
# 3. runcmd wrote the marker to /var/lib/shop-data/ready, a folder that
#    doesn't exist ("touch: cannot touch ... No such file or directory" in
#    the output log). The marker belongs at /var/lib/shop/ready, in the
#    folder the image has.
# The corrected user data, then a fresh launch, because the per-instance
# steps only run on a new instance. In the lab you'd edit the file with nano.
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
cloud-init status --long
