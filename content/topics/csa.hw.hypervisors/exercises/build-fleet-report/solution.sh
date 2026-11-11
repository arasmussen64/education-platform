mkdir -p ~/bin ~/report
cat > ~/bin/fleet-report <<'EOF'
#!/bin/bash
# fleet-report: one line per server in a fleet folder: its name, what it
# runs on, and how its network card reaches the hardware.
# Usage: fleet-report FLEET_DIR
set -euo pipefail
fleet="${1:?usage: fleet-report FLEET_DIR}"

for dir in "$fleet"/*/; do
  dir="${dir%/}"
  name=$(basename "$dir")

  # What it runs on: the vm line of systemd-detect-virt, never the "any"
  # line, which names a container before the VM under it.
  vm=$(awk -F': ' '$1 == "vm" {print $2}' "$dir/detect-virt.txt")
  case "$vm" in
    microsoft) runs_on=hyperv ;;
    kvm | amazon | google) runs_on=kvm ;;
    *) runs_on=$vm ;;
  esac

  # How the network card reaches the hardware: the fastest path among all
  # of its interfaces, whatever order they are listed in.
  path=none
  while read -r _ driver; do
    case "$driver" in
      mlx4_core | mlx5_core | mana | ena | ixgbevf | iavf)
        path=sriov ;;
      virtio_net | hv_netvsc | vif | vmxnet3 | gve)
        if [ "$path" != sriov ]; then path=paravirtual; fi ;;
      e1000 | e1000e | 8139cp | 8139too | pcnet32 | ne2k-pci)
        if [ "$path" = none ]; then path=emulated; fi ;;
    esac
  done < "$dir/net-drivers.txt"

  echo "$name $runs_on $path"
done | sort
EOF
chmod +x ~/bin/fleet-report
~/bin/fleet-report /srv/fleet-a
~/bin/fleet-report /srv/fleet-a | awk '$3 == "emulated" {print $1}' > ~/report/slow.txt
cat ~/report/slow.txt
