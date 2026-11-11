# Wrong: the report for the shop's own fleet, typed in by hand. It is right
# for /srv/fleet-a and for no other fleet.
mkdir -p ~/bin ~/report
cat > ~/bin/fleet-report <<'EOF'
#!/bin/bash
cat <<'REPORT'
api-1 hyperv sriov
batch-1 hyperv paravirtual
db-1 kvm paravirtual
legacy-1 qemu emulated
print-1 qemu emulated
web-1 kvm sriov
REPORT
EOF
chmod +x ~/bin/fleet-report
printf 'legacy-1\nprint-1\n' > ~/report/slow.txt
