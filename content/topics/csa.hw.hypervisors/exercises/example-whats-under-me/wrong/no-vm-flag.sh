# Wrong: line 1 saved without --vm, so it names the innermost layer (WSL's
# container, or docker) instead of the VM under it.
mkdir -p ~/example
{ systemd-detect-virt || true; awk -F': ' '$1 == "vm" {print $2}' /srv/captures/qemu-virtio/detect-virt.txt; } > ~/example/under-me.txt
/opt/vm/boot-default | tee ~/example/boot.log
