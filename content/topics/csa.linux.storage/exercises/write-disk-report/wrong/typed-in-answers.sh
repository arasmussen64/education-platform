# Wrong: the four answers for /srv/shop were worked out once and typed in,
# so the script prints the same lines whatever it is asked about. (The
# unquoted EOF makes the two df commands run now, while the file is being
# written, and puts their output in it as plain text.)
mkdir -p ~/bin
cat > ~/bin/disk-report <<EOF
#!/bin/bash
echo "used: $(df --output=pcent /srv/shop | tail -n 1 | tr -d ' ')"
echo "inodes: $(df --output=ipcent /srv/shop | tail -n 1 | tr -d ' ')"
echo "biggest: /srv/shop/logs"
echo "deleted but open: 1"
EOF
chmod +x ~/bin/disk-report
