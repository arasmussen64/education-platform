# The finished script. In the lab you'd fill the four gaps with nano; here
# it's written in one go.
cat > ~/bin/under-me <<'EOF'
#!/bin/bash
# under-me: what a recorded machine runs on, and how its network cards and
# disks reach the hardware, from a folder that lab-capture wrote.
# Usage: under-me CAPTURE_DIR
set -euo pipefail
dir="${1:?usage: under-me CAPTURE_DIR}"

# The hypervisor's vendor, as lscpu names it, or "none" when lscpu names none.
vendor=$(awk -F': *' '$1 == "Hypervisor vendor" {print $2}' "$dir/lscpu.txt")
echo "vendor: ${vendor:-none}"

# The VM under the machine, even when the capture was taken in a container.
echo "vm: $(awk -F': ' '$1 == "vm" {print $2}' "$dir/detect-virt.txt")"

# The driver behind each network card and each disk, sorted, each named once.
echo "nics: $(awk '{print $2}' "$dir/net-drivers.txt" | sort -u | paste -sd ' ')"
echo "disks: $(awk '{print $2}' "$dir/block-drivers.txt" | sort -u | paste -sd ' ')"
EOF
~/bin/under-me /srv/captures/laptop-wsl2
~/bin/under-me /srv/captures/qemu-two-nics
sudo lab-capture ~/captures/here
~/bin/under-me ~/captures/here
