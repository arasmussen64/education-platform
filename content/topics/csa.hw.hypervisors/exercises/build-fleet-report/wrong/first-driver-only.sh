# Wrong: only the first interface listed is read, so a server whose virtual
# function is listed after its synthetic interface looks paravirtual.
mkdir -p ~/bin ~/report
cat > ~/bin/fleet-report <<'EOF'
#!/bin/bash
set -euo pipefail
for dir in "$1"/*/; do
  dir="${dir%/}"
  vm=$(awk -F': ' '$1 == "vm" {print $2}' "$dir/detect-virt.txt")
  case "$vm" in
    microsoft) runs_on=hyperv ;;
    kvm | amazon | google) runs_on=kvm ;;
    *) runs_on=$vm ;;
  esac
  driver=$(awk 'NR == 1 {print $2}' "$dir/net-drivers.txt")
  case "$driver" in
    mlx4_core | mlx5_core | mana | ena | ixgbevf | iavf) path=sriov ;;
    virtio_net | hv_netvsc | vif | vmxnet3 | gve) path=paravirtual ;;
    *) path=emulated ;;
  esac
  echo "$(basename "$dir") $runs_on $path"
done | sort
EOF
chmod +x ~/bin/fleet-report
~/bin/fleet-report /srv/fleet-a | awk '$3 == "emulated" {print $1}' > ~/report/slow.txt
