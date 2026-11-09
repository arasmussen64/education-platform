# Wrong: run as a service but with no quota, so it takes a whole CPU and is
# never throttled.
sudo systemd-run --unit=spin spin
sleep 3
mkdir -p ~/example && grep throttled /sys/fs/cgroup/system.slice/spin.service/cpu.stat > ~/example/throttled.txt && sudo systemctl stop spin
