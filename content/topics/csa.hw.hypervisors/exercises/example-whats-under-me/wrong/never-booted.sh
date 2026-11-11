# Wrong: both answers saved, but the VM never booted, so there is no guest
# report.
mkdir -p ~/example
{ systemd-detect-virt --vm || true; awk -F': ' '$1 == "vm" {print $2}' /srv/captures/qemu-virtio/detect-virt.txt; } > ~/example/under-me.txt
