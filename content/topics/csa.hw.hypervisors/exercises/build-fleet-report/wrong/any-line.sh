# Wrong: "what it runs on" read from systemd-detect-virt's "any" line, which
# names the innermost layer: for a capture taken in a container, that is the
# container (docker), not the VM it runs on.
mkdir -p ~/bin ~/report
cat > ~/bin/fleet-report <<'EOF'
#!/bin/bash
set -euo pipefail
for dir in "$1"/*/; do
  dir="${dir%/}"
  vm=$(awk -F': ' '$1 == "any" {print $2}' "$dir/detect-virt.txt")
  case "$vm" in
    microsoft) runs_on=hyperv ;;
    kvm | amazon | google) runs_on=kvm ;;
    *) runs_on=$vm ;;
  esac
  path=none
  while read -r _ driver; do
    case "$driver" in
      mlx4_core | mlx5_core | mana | ena | ixgbevf | iavf) path=sriov ;;
      virtio_net | hv_netvsc | vif | vmxnet3 | gve)
        if [ "$path" != sriov ]; then path=paravirtual; fi ;;
      e1000 | e1000e | 8139cp | 8139too | pcnet32 | ne2k-pci)
        if [ "$path" = none ]; then path=emulated; fi ;;
    esac
  done < "$dir/net-drivers.txt"
  echo "$(basename "$dir") $runs_on $path"
done | sort
EOF
chmod +x ~/bin/fleet-report
~/bin/fleet-report /srv/fleet-a | awk '$3 == "emulated" {print $1}' > ~/report/slow.txt
