# Wrong: the report is right, but slow.txt names every server in the fleet,
# not only the ones on an emulated card.
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
ls /srv/fleet-a > ~/report/slow.txt
