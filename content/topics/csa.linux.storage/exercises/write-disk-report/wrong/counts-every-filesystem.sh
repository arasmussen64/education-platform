# Wrong: the deleted-but-open line counts every deleted file on the
# machine, not just the ones on the filesystem it was asked about.
mkdir -p ~/bin
cat > ~/bin/disk-report <<'EOF'
#!/bin/bash
mount="$1"
echo "used: $(df --output=pcent "$mount" | tail -n 1 | tr -d ' ')"
echo "inodes: $(df --output=ipcent "$mount" | tail -n 1 | tr -d ' ')"
echo "biggest: $(sudo du -sk "$mount"/* | sort -rn | head -n 1 | cut -f2)"
echo "deleted but open: $(sudo lsof +L1 2>/dev/null | grep -c '(deleted)')"
EOF
chmod +x ~/bin/disk-report
