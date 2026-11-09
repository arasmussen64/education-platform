# Wrong: the quota and the numbers are right, but the spinner is left
# burning its fifth of a CPU forever.
sudo systemd-run --unit=spin -p CPUQuota=20% spin
sleep 3
mkdir -p ~/example && grep throttled /sys/fs/cgroup/system.slice/spin.service/cpu.stat > ~/example/throttled.txt
