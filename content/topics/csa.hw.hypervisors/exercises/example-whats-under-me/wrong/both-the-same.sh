# Wrong: this machine's answer written twice; the recording was never read.
mkdir -p ~/example
{ systemd-detect-virt --vm || true; systemd-detect-virt --vm || true; } > ~/example/under-me.txt
/opt/vm/boot-default | tee ~/example/boot.log
