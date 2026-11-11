# Wrong: no fallback when lscpu names no vendor, so a QEMU guest under
# emulation gets an empty vendor line instead of "none".
cat > ~/bin/under-me <<'EOF'
#!/bin/bash
set -euo pipefail
dir="${1:?usage: under-me CAPTURE_DIR}"
vendor=$(awk -F': *' '$1 == "Hypervisor vendor" {print $2}' "$dir/lscpu.txt")
echo "vendor: $vendor"
echo "vm: $(awk -F': ' '$1 == "vm" {print $2}' "$dir/detect-virt.txt")"
echo "nics: $(awk '{print $2}' "$dir/net-drivers.txt" | sort -u | paste -sd ' ')"
echo "disks: $(awk '{print $2}' "$dir/block-drivers.txt" | sort -u | paste -sd ' ')"
EOF
