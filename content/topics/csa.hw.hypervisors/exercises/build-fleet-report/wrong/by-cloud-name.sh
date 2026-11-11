# Wrong: the path guessed from the cloud ("Azure means SR-IOV") instead of
# read from the drivers. An Azure VM without Accelerated Networking has only
# the synthetic, paravirtual interface.
mkdir -p ~/bin ~/report
cat > ~/bin/fleet-report <<'EOF'
#!/bin/bash
set -euo pipefail
for dir in "$1"/*/; do
  dir="${dir%/}"
  vm=$(awk -F': ' '$1 == "vm" {print $2}' "$dir/detect-virt.txt")
  case "$vm" in
    microsoft) echo "$(basename "$dir") hyperv sriov" ;;
    amazon) echo "$(basename "$dir") kvm sriov" ;;
    google | kvm) echo "$(basename "$dir") kvm paravirtual" ;;
    xen) echo "$(basename "$dir") xen paravirtual" ;;
    qemu) echo "$(basename "$dir") qemu emulated" ;;
    *) echo "$(basename "$dir") $vm none" ;;
  esac
done | sort
EOF
chmod +x ~/bin/fleet-report
~/bin/fleet-report /srv/fleet-a | awk '$3 == "emulated" {print $1}' > ~/report/slow.txt
