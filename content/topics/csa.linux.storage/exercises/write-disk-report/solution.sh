# The reference script, written in one go; in the lab you'd use nano.
mkdir -p ~/bin
cat > ~/bin/disk-report <<'EOF'
#!/bin/bash
# Usage: disk-report MOUNTPOINT
# Four lines about a filesystem: how full it is in bytes and in inodes, its
# biggest top-level folder, and how many deleted files are still held open
# on it (space df counts but du can't find).
mount="$1"
echo "used: $(df --output=pcent "$mount" | tail -n 1 | tr -d ' ')"
echo "inodes: $(df --output=ipcent "$mount" | tail -n 1 | tr -d ' ')"
echo "biggest: $(sudo du -sk "$mount"/* | sort -rn | head -n 1 | cut -f2)"
echo "deleted but open: $(sudo lsof +L1 2>/dev/null | grep -c " $mount/")"
EOF
chmod +x ~/bin/disk-report
~/bin/disk-report /srv/shop
~/bin/disk-report /srv/media
