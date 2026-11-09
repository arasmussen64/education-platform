# Wrong: lsof without sudo sees only your own processes, so the deleted log
# another process holds is never counted.
mkdir -p ~/bin
cat > ~/bin/disk-report <<'EOF'
#!/bin/bash
mount="$1"
echo "used: $(df --output=pcent "$mount" | tail -n 1 | tr -d ' ')"
echo "inodes: $(df --output=ipcent "$mount" | tail -n 1 | tr -d ' ')"
echo "biggest: $(sudo du -sk "$mount"/* | sort -rn | head -n 1 | cut -f2)"
echo "deleted but open: $(lsof +L1 2>/dev/null | grep -c " $mount/")"
EOF
chmod +x ~/bin/disk-report
