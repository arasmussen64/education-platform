# Wrong: df is asked about the root filesystem, not the one named.
mkdir -p ~/bin
cat > ~/bin/disk-report <<'EOF'
#!/bin/bash
mount="$1"
echo "used: $(df --output=pcent / | tail -n 1 | tr -d ' ')"
echo "inodes: $(df --output=ipcent / | tail -n 1 | tr -d ' ')"
echo "biggest: $(sudo du -sk "$mount"/* | sort -rn | head -n 1 | cut -f2)"
echo "deleted but open: $(sudo lsof +L1 2>/dev/null | grep -c " $mount/")"
EOF
chmod +x ~/bin/disk-report
