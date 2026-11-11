# Wrong: the drivers listed as the files have them, unsorted and repeated:
# the laptop's five disks give "sd sd sd sd sd".
cat > ~/bin/under-me <<'EOF'
#!/bin/bash
set -euo pipefail
dir="${1:?usage: under-me CAPTURE_DIR}"
vendor=$(awk -F': *' '$1 == "Hypervisor vendor" {print $2}' "$dir/lscpu.txt")
echo "vendor: ${vendor:-none}"
echo "vm: $(awk -F': ' '$1 == "vm" {print $2}' "$dir/detect-virt.txt")"
echo "nics: $(awk '{print $2}' "$dir/net-drivers.txt" | paste -sd ' ')"
echo "disks: $(awk '{print $2}' "$dir/block-drivers.txt" | paste -sd ' ')"
EOF
