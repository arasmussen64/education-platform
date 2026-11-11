# Wrong: the vm line read from systemd-detect-virt's "any" line, which names
# the innermost layer: on the laptop capture that's WSL's container, not the
# Hyper-V VM under it.
cat > ~/bin/under-me <<'EOF'
#!/bin/bash
set -euo pipefail
dir="${1:?usage: under-me CAPTURE_DIR}"
vendor=$(awk -F': *' '$1 == "Hypervisor vendor" {print $2}' "$dir/lscpu.txt")
echo "vendor: ${vendor:-none}"
echo "vm: $(awk -F': ' '$1 == "any" {print $2}' "$dir/detect-virt.txt")"
echo "nics: $(awk '{print $2}' "$dir/net-drivers.txt" | sort -u | paste -sd ' ')"
echo "disks: $(awk '{print $2}' "$dir/block-drivers.txt" | sort -u | paste -sd ' ')"
EOF
