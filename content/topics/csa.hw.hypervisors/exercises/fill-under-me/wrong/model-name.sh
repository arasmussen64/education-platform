# Wrong: the CPU's model name read as the hypervisor's vendor. The model is
# the processor the guest is shown, not who is running it.
cat > ~/bin/under-me <<'EOF'
#!/bin/bash
set -euo pipefail
dir="${1:?usage: under-me CAPTURE_DIR}"
vendor=$(awk -F': *' '$1 == "Model name" {print $2}' "$dir/lscpu.txt")
echo "vendor: ${vendor:-none}"
echo "vm: $(awk -F': ' '$1 == "vm" {print $2}' "$dir/detect-virt.txt")"
echo "nics: $(awk '{print $2}' "$dir/net-drivers.txt" | sort -u | paste -sd ' ')"
echo "disks: $(awk '{print $2}' "$dir/block-drivers.txt" | sort -u | paste -sd ' ')"
EOF
